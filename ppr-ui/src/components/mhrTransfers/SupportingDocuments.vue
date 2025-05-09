<template>
  <div
    id="supporting-documents"
    class="pb-3"
  >
    <p
      class="fs-16"
      :class="{ 'error-text': showDocumentsSelectionError }"
    >
      Select the supporting document you have for this owner:
    </p>
    <v-radio-group
      id="supporting-docs-options"
      v-model="deletedOwnerState.supportingDocument"
      class="supporting-docs-options"
      inline
      :disabled="isGlobalEditingMode"
      :hide-details="true"
    >
      <v-radio
        id="supporting-doc-option-one"
        :label="docOptions.optionOne.text"
        :value="docOptions.optionOne.value"
        class="non-clickable-label"
        data-test-id="supporting-doc-option-one"
      />
      <v-radio
        id="supporting-doc-option-two"
        :label="docOptions.optionTwo.text"
        :class="{ 'invalid-selection': isSecondOptionError }"
        :value="docOptions.optionTwo.value"
        :disabled="isSecondOptionDisabled"
        :color="isSecondOptionError ? 'error' : 'primary'"
        class="non-clickable-label"
        data-test-id="supporting-doc-option-two"
      />
    </v-radio-group>
    <div
      v-if="deletedOwnerState.supportingDocument === docOptions.optionOne.value"
      class="supporting-doc-one"
    >
      <p class="fs-16">
        <strong>Note:</strong> {{ docOptions.optionOne.note }}
      </p>
      <slot
        v-if="hasDeathCertForFirstOption"
        name="deathCert"
      />
    </div>
    <div
      v-if="deletedOwnerState.supportingDocument === docOptions.optionTwo.value"
      class="supporting-doc-two"
    >
      <slot name="deathCert" />
    </div>
  </div>
</template>

<script lang="ts">
import { useHomeOwners, useTransferOwners } from '@/composables'
import { SupportingDocumentsOptions } from '@/enums/transferTypes'
import type { MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { defineComponent, reactive, toRefs, watch, computed, onUpdated } from 'vue'
import { useStore } from '@/store/store'
import { transferSupportingDocuments } from '@/resources/'

export default defineComponent({
  name: 'SupportingDocument',
  components: { },
  props: {
    deletedOwner: {
      type: Object as () => MhrRegistrationHomeOwnerIF,
      required: true
    },
    // validate the supporting document selection
    validate: {
      type: Boolean,
      default: false
    },
    // Used to disable Death Cert when group has only one owner
    isSecondOptionDisabled: {
      type: Boolean,
      default: false
    },
    // Used to show error for Death Cert radio button
    isSecondOptionError: {
      type: Boolean,
      default: false
    },
    hasDeathCertForFirstOption: {
      type: Boolean,
      default: false
    }
  },
  emits: ['handleDocOptionOneSelected'],
  setup (props, { emit }) {
    const { editHomeOwner, isGlobalEditingMode } = useHomeOwners(true)
    const { getMhrTransferType } = useTransferOwners()
    const { setUnsavedChanges } = useStore()

    // Update deleted Owner based on supporting document selection
    // Only death certificate is captured in the api
    const updateDeletedOwner = (): void => {
      editHomeOwner({
        ...localState.deletedOwnerState
      },
      localState.deletedOwnerState.groupId
      )
      setUnsavedChanges(true)
    }

    onUpdated(() => {
      localState.deletedOwnerState = props.deletedOwner
    })

    const localState = reactive({
      deletedOwnerState: props.deletedOwner as MhrRegistrationHomeOwnerIF,
      showDocumentsSelectionError: computed(() => {
        return props.validate && !localState.deletedOwnerState.supportingDocument
      }),
      // Get relevant supporting documents options based on transfer type from the Resources
      docOptions: transferSupportingDocuments[getMhrTransferType.value.transferType]
    })

    // When there is one owner in the group, pre-select first radio option
    if (props.isSecondOptionDisabled) {
      localState.deletedOwnerState.supportingDocument = localState.docOptions.optionOne.value
      updateDeletedOwner()
    }

    watch(() => localState.deletedOwnerState.supportingDocument, () => {
      updateDeletedOwner()
      // Only one Grant of Probate document can be selected for the group
      if (localState.deletedOwnerState.supportingDocument === SupportingDocumentsOptions.PROBATE_GRANT ||
        localState.deletedOwnerState.supportingDocument === SupportingDocumentsOptions.AFFIDAVIT ||
        localState.deletedOwnerState.supportingDocument === SupportingDocumentsOptions.ADMIN_GRANT) {
        emit('handleDocOptionOneSelected')
      }
    })

    return {
      SupportingDocumentsOptions,
      isGlobalEditingMode,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.supporting-docs-options {
  display: flex;
  flex-direction: column;

  :deep(.non-clickable-label .v-label) {
    pointer-events: none;
  }

  .v-radio {
    flex: 1;
    background-color: rgba(0, 0, 0, 0.06);
    height: 60px;
    padding-left: 24px;
    margin-right: 20px;
  }

  .v-radio:last-of-type {
    margin-right: 0;
  }

  .v-radio--is-disabled {
    opacity: 0.4;
  }

  .invalid-selection {
    border: 1px solid $error;
    background-color: white;
    .error--text {
      color: $error;
    }
  }

  .selected-radio {
    border: 1px solid $app-blue;
    background-color: white;
  }

  .selected-radio.invalid-selection {
    border: 1px solid $error;
  }

}

.supporting-doc-one,
.supporting-doc-two {
  border-top: 1px solid $gray3;
  margin-top: 35px;
  padding-top: 35px;
  white-space: normal;
}

.supporting-doc-two {
  padding-top: 22px;
  .death-certificate {
    margin-bottom: 0;
  }
}
</style>
