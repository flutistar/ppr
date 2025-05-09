import type { OrgLookupConfigIF } from '@/interfaces'
import { MhrSubTypes } from '@/enums'

export const UserAccessOrgLookupConfig: Record<MhrSubTypes, OrgLookupConfigIF> = {
  [MhrSubTypes.LAWYERS_NOTARIES]: {
    pluralTitle: 'Qualified Supplier\'s',
    lookupSubtitle: 'You can find the full legal name of an active B.C. business by entering the name or ' +
      'incorporation number of the business, or you can type the full legal name of the Qualified Supplier if it is ' +
      'not a registered B.C. business.',
    fieldLabel: 'Find or Enter the Full Legal Name of the Business',
    fieldHint: 'Example: Legal business name of lawyer, notary or law firm',
    nilSearchText: 'If the Qualified Supplier is not a registered B.C. business, enter the complete business name.',
    disableManualBusLookup: false,
    addressSubtitle: ''
  },
  [MhrSubTypes.MANUFACTURER]: {
    pluralTitle: 'Home Manufacturer\'s',
    lookupSubtitle: 'You can find the full legal name of an active B.C. business by entering the name or ' +
      'incorporation number of the business. Must be an active registered B.C. business.',
    fieldLabel: 'Find the Full Legal Name of the Business',
    fieldHint: 'Example: ABC Homes Canada Inc. ',
    nilSearchText: '',
    disableManualBusLookup: true,
    dbaLookupSubtitle: 'If entered, this name will display next to the Legal Business Name for Registered Location ' +
      'and Description of Manufactured Home in registration documents.',
    dbaFieldLabel: 'Find or enter the DBA or Operating Name (Optional)',
    dbaFieldHint: 'Example: Westcoast Homes',
    dbaNilSearchText: 'If the business is not a registered DBA (Doing Business As), enter the complete business name.',
    addressSubtitle: 'This address will display as the registered owner’s mailing address for homes owned by this ' +
      'manufacturer.'
  },
  [MhrSubTypes.DEALERS]: {
    pluralTitle: 'Home Dealer\'s',
    lookupSubtitle: 'You can find the full legal name of an active B.C. business by entering the name or ' +
      'incorporation number of the business. Must be an active registered B.C. business.',
    fieldLabel: 'Find the Full Legal Name of the Business',
    fieldHint: '',
    nilSearchText: '',
    disableManualBusLookup: true,
    dbaLookupSubtitle: 'If the home dealer uses a DBA (Doing Business As) or Operating Name that is different than ' +
      'the Legal Business Name, find or enter the name.',
    dbaFieldLabel: 'Find or enter the DBA or Operating Name (Optional)',
    dbaFieldHint: '',
    dbaNilSearchText: 'If the business is not a registered DBA (Doing Business As), enter the complete business name.',
    addressSubtitle: ''
  },
  [MhrSubTypes.QUALIFIED_SUPPLIER]: {
    fieldLabel: '',
    fieldHint: '',
    nilSearchText: ''
  },
  [MhrSubTypes.GENERAL_PUBLIC]: {
    fieldLabel: '',
    fieldHint: '',
    nilSearchText: ''
  }
}
