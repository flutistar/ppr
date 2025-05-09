# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper methods for saving draft and registration info when payment is by credit card."""
from sqlalchemy.sql import text

from mhr_api.models import MhrDescription, MhrDocument, MhrDraft, MhrLocation, MhrNote, MhrParty, MhrRegistration, db
from mhr_api.models import registration_change_utils as change_utils
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models import utils as model_utils
from mhr_api.models.mhr_draft import DRAFT_PAY_PENDING_PREFIX
from mhr_api.models.mhr_registration import REG_TO_DOC_TYPE
from mhr_api.models.type_tables import (
    MhrDocumentTypes,
    MhrNoteStatusTypes,
    MhrPartyTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationTypes,
)
from mhr_api.services.authz import STAFF_ROLE
from mhr_api.utils.logging import logger

DRAFT_QUERY_PKEYS = """
select get_mhr_draft_number() AS draft_num,
       nextval('mhr_draft_id_seq') AS draft_id
"""


def create_new_draft(json_data: dict) -> MhrDraft:
    """Get db generated identifiers for a new MHR draft record.

    Get draft_number and draft ID.
    """
    query_text = DRAFT_QUERY_PKEYS
    draft: MhrDraft = MhrDraft()
    draft.draft = json_data
    draft.account_id = json_data.get("accountId")
    draft.create_ts = model_utils.now_ts()
    draft.registration_type = json_data.get("registrationType")
    query = text(query_text)
    result = db.session.execute(query)
    row = result.first()
    draft.draft_number = DRAFT_PAY_PENDING_PREFIX + str(row[0])
    draft.id = int(row[1])
    logger.info(f"New draft created id={draft.id} number={draft.draft_number}")
    return draft


def save_change_cc_draft(base_reg: MhrRegistration, json_data: dict) -> MhrRegistration:
    """
    Change registration with credit card payment create/update draft. Returns an unsaved registration
    with response JSON.

    Args:
        base_reg (MhrRegistration): current registration being updated.
        json_data (dict): Request payload updated with some extra registration information (payment).
    """
    # Create or update draft.
    draft: MhrDraft = MhrDraft.find_draft(json_data)
    registration: MhrRegistration = MhrRegistration()
    json_data["paymentPending"] = True
    current_status: str = base_reg.status_type
    json_data["status"] = current_status
    if not json_data.get("mhrNumber"):
        json_data["mhrNumber"] = base_reg.mhr_number
    if draft:
        draft.draft = json_data
        draft.draft_number = DRAFT_PAY_PENDING_PREFIX + draft.draft_number
    else:
        draft = create_new_draft(json_data)
    draft.update_ts = model_utils.now_ts()
    draft.user_id = json_data["payment"].get("invoiceId")
    draft.mhr_number = base_reg.mhr_number
    draft.save()
    registration.draft = draft
    registration.reg_json = json_data
    logger.info("Created minimal registration with saved draft: return draft.json in response.")
    # Lock the base registration here:
    base_reg.status_type = MhrRegistrationStatusTypes.DRAFT.value
    logger.info(f"Locking mhr {draft.mhr_number}: status changed from {current_status} to {base_reg.status_type}.")
    base_reg.save()

    return registration


def save_new_cc_draft(json_data: dict) -> MhrRegistration:
    """
    New registration with credit card payment create/update draft. Returns an unsaved registration
    with response JSON.

    Args:
        json_data (dict): Request payload updated with some extra registration information (payment).
    """
    # Create or update draft.
    draft: MhrDraft = MhrDraft.find_draft(json_data)
    registration: MhrRegistration = MhrRegistration()
    json_data["paymentPending"] = True
    if draft:
        draft.draft = json_data
        draft.draft_number = DRAFT_PAY_PENDING_PREFIX + draft.draft_number
    else:
        draft = create_new_draft(json_data)
    draft.update_ts = model_utils.now_ts()
    draft.user_id = json_data["payment"].get("invoiceId")
    draft.save()
    registration.draft = draft
    registration.reg_json = json_data
    logger.info("Created minimal registration with saved draft: return draft.json in response.")
    return registration


def create_basic_registration(draft: MhrDraft) -> MhrRegistration:
    """Create new home registration from the draft."""
    draft_json = draft.draft
    registration: MhrRegistration = MhrRegistration(
        registration_type=draft.registration_type, account_id=draft.account_id, user_id=draft_json.get("username")
    )
    reg_vals: MhrRegistration = None
    if draft.registration_type == MhrRegistrationTypes.MHREG.value:
        reg_vals = reg_utils.get_generated_values(
            MhrRegistration(), draft, draft_json.get("usergroup"), draft_json.get("documentId")
        )
        registration.mhr_number = reg_vals.mhr_number
    else:
        reg_vals = reg_utils.get_change_generated_values(
            MhrRegistration(), draft, draft_json.get("usergroup"), draft_json.get("documentId")
        )
        registration.mhr_number = draft.mhr_number
    registration.doc_reg_number = reg_vals.doc_reg_number
    registration.id = reg_vals.id  # pylint: disable=invalid-name; allow name of id.
    registration.doc_pkey = reg_vals.doc_pkey
    registration.registration_ts = model_utils.now_ts()
    registration.status_type = MhrRegistrationStatusTypes.ACTIVE
    if draft_json.get("documentId"):
        registration.doc_id = draft_json.get("documentId")
    else:
        registration.doc_id = reg_vals.doc_id
        draft_json["documentId"] = registration.doc_id
    registration.pay_invoice_id = int(draft_json["payment"].get("invoiceId"))
    registration.pay_path = draft_json["payment"].get("receipt")
    registration.draft_id = draft.id
    registration.draft = draft
    registration.reg_json = draft_json
    registration.client_reference_id = draft_json.get("clientReferenceId")
    doc: MhrDocument = MhrDocument.create_from_json(
        registration, draft_json, REG_TO_DOC_TYPE[registration.registration_type]
    )
    doc.registration_id = registration.id
    if registration.registration_type == MhrRegistrationTypes.REG_STAFF_ADMIN and draft_json.get("documentType"):
        doc.document_type = draft_json.get("documentType")
    elif registration.registration_type == MhrRegistrationTypes.REG_NOTE and draft_json.get("note"):
        doc.document_type = draft_json["note"].get("documentType")
    elif registration.registration_type == MhrRegistrationTypes.TRANS and draft_json.get("transferDocumentType"):
        doc.document_type = draft_json.get("transferDocumentType")
    registration.documents = [doc]
    registration.parties = MhrParty.create_from_registration_json(draft_json, registration.id)
    logger.info(f"New registration created id={registration.id} mhr#={registration.mhr_number}")
    return registration


def create_new_registration(draft: MhrDraft) -> MhrRegistration:
    """Create new home registration from the draft."""
    logger.info("Create new registration starting")
    registration: MhrRegistration = create_basic_registration(draft)
    json_data = draft.draft
    registration.create_new_groups(json_data)
    registration.locations = [MhrLocation.create_from_json(json_data["location"], registration.id)]
    description: MhrDescription = MhrDescription.create_from_json(json_data.get("description"), registration.id)
    registration.descriptions = [description]
    registration.sections = MhrRegistration.get_sections(json_data, registration.id)
    registration.save()
    logger.info(f"New reg id={registration.id} type={registration.registration_type}, mhr#={registration.mhr_number}")
    return registration


def create_permit_registration(
    json_data: dict, current_reg: MhrRegistration, new_reg: MhrRegistration
) -> MhrRegistration:
    """Create new transport permit registration from the draft."""
    doc: MhrDocument = new_reg.documents[0]
    if json_data.get("amendment"):
        json_data["registrationType"] = MhrRegistrationTypes.AMENDMENT
        doc.document_type = MhrDocumentTypes.AMEND_PERMIT
        new_reg.registration_type = MhrRegistrationTypes.AMENDMENT
    elif json_data.get("extension"):
        doc.document_type = MhrDocumentTypes.REG_103E
        new_reg.registration_type = MhrRegistrationTypes.PERMIT_EXTENSION
    # Save permit expiry date as a note.
    note: MhrNote = MhrNote(
        registration_id=current_reg.id,
        document_id=doc.id,
        document_type=doc.document_type,
        destroyed="N",
        status_type=MhrNoteStatusTypes.ACTIVE,
        remarks="",
        change_registration_id=new_reg.id,
        expiry_date=model_utils.compute_permit_expiry(),
    )
    # Amendment use existing expiry timestamp
    if json_data.get("amendment"):
        for reg in current_reg.change_registrations:  # Updating a change registration location.
            if (
                reg.notes
                and reg.notes[0]
                and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
                and reg.notes[0].expiry_date
                and reg.notes[0].document_type
                in (MhrDocumentTypes.REG_103, MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT)
            ):
                note.expiry_date = reg.notes[0].expiry_date
    if doc.document_type == MhrDocumentTypes.REG_103E:  # Same location with optional updated tax info.
        change_utils.setup_permit_extension_location(current_reg, new_reg, json_data.get("newLocation"))
        if json_data.get("accountId") == STAFF_ROLE and json_data.get("note") and json_data["note"].get("remarks"):
            note.remarks = json_data["note"].get("remarks")
    else:  # New location
        new_reg.locations.append(MhrLocation.create_from_json(json_data.get("newLocation"), new_reg.id))
    new_reg.notes = [note]
    new_reg.save()
    if current_reg.id and current_reg.id > 0 and current_reg.locations:
        change_utils.save_permit(current_reg, json_data, new_reg.id)
    return new_reg


def create_transfer_registration(
    json_data: dict, current_reg: MhrRegistration, new_reg: MhrRegistration
) -> MhrRegistration:
    """Create new transfer of ownership registration from the draft."""
    if current_reg.owner_groups:
        new_reg.add_new_groups(json_data, reg_utils.get_owner_group_count(current_reg))
    new_reg.save()
    if current_reg.id and current_reg.id > 0 and current_reg.owner_groups:
        current_reg.save_transfer(json_data, new_reg.id)
    elif MhrRegistration.is_exre_transfer(current_reg, json_data):
        current_reg.save_transfer(json_data, new_reg.id)
    return new_reg


def create_exemption_registration(
    json_data: dict, current_reg: MhrRegistration, new_reg: MhrRegistration
) -> MhrRegistration:
    """Create new exemption registration from the draft."""
    if json_data.get("note"):
        if json_data["note"].get("givingNoticeParty"):
            notice_json = json_data["note"]["givingNoticeParty"]
            new_reg.parties.append(MhrParty.create_from_json(notice_json, MhrPartyTypes.CONTACT, new_reg.id))
        doc: MhrDocument = new_reg.documents[0]
        new_reg.notes = [
            MhrNote.create_from_json(json_data.get("note"), current_reg.id, doc.id, new_reg.registration_ts, new_reg.id)
        ]
    new_reg.save()
    current_reg.save_exemption(new_reg.id)
    return new_reg


def create_change_registration(draft: MhrDraft, current_reg: MhrRegistration) -> MhrRegistration:
    """Create new change registration from the draft."""
    new_reg: MhrRegistration = create_basic_registration(draft)
    new_reg.documents[0].registration_id = current_reg.id
    draft_json = draft.draft
    if draft.registration_type == MhrRegistrationTypes.PERMIT.value:
        new_reg = create_permit_registration(draft_json, current_reg, new_reg)
    elif draft.registration_type == MhrRegistrationTypes.TRANS.value:
        new_reg = create_transfer_registration(draft_json, current_reg, new_reg)
    elif draft.registration_type in (
        MhrRegistrationTypes.EXEMPTION_NON_RES.value,
        MhrRegistrationTypes.EXEMPTION_RES.value,
    ):
        new_reg = create_exemption_registration(draft_json, current_reg, new_reg)
    logger.info(f"New reg id={new_reg.id} type={new_reg.registration_type}, mhr#={new_reg.mhr_number}")
    return new_reg
