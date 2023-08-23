<template>
  <div id="service-agreement">
    <!-- download service agreement button -->
    <v-btn outlined color="primary" class="mt-2" :ripple="false" @click="downloadServiceAgreement">
      <img alt="" src="@/assets/svgs/pdf-icon-blue.svg" />
      <span class="pl-1">Download Qualified Suppliers' Agreement</span>
    </v-btn>

    <!-- service agreement preview container -->
    <v-card flat class="mt-10 scroll-container">
      <!-- TODO: Design Currently reviewing pdf preview options - Placeholder & Example implementation below -->
      <label>Document Preview/html Placeholder</label>
      <!--          <vue-pdf-embed v-if="serviceAgreementUrl" :source="serviceAgreementUrl" />-->
      <!--          <v-progress-circular v-else class="loading-spinner" color="primary" size="50" indeterminate ce/>-->
    </v-card>

    <!-- service agreement confirmation -->
    <v-card flat class="mt-5 pa-8" :class="{'border-error-left': showQsSaConfirmError}">
      <v-checkbox
        class="align-start ma-0 pa-0"
        color="primary"
        hide-details
        v-model="serviceAgreementConfirm"
      >
        <template v-slot:label>
          <span :class="{ 'error-text': showQsSaConfirmError }">
            I have read, understood and agree to the terms and conditions of the Qualified Suppliers’ Agreement
           for the Manufactured Home Registry.
          </span>
        </template>
      </v-checkbox>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, toRefs, watch } from 'vue-demi'
import { useUserAccess } from '@/composables'
import { getQsServiceAgreements } from '@/utils'
import { useStore } from '@/store/store'

export default defineComponent({
  name: 'ServiceAgreement',
  components: {
  },
  props: { validate: { type: Boolean, default: false } },
  setup (props) {
    const { setMhrQsValidation } = useStore()
    const { downloadServiceAgreement } = useUserAccess()

    const localState = reactive({
      showQsSaConfirmError: false,
      serviceAgreementUrl: '',
      serviceAgreementConfirm: false
    })

    onMounted(async () => {
      // Get the service agreement pdf url for preview
      const serviceAgreementBlob = await getQsServiceAgreements()
      localState.serviceAgreementUrl = URL.createObjectURL(serviceAgreementBlob)
    })

    watch(() => localState.serviceAgreementConfirm, (val: boolean) => {
      localState.showQsSaConfirmError = !val && props.validate
      setMhrQsValidation({ key: 'qsSaConfirmValid', value: val })
    })

    watch(() => props.validate, (val: boolean) => {
      localState.showQsSaConfirmError = val
    })

    return {
      downloadServiceAgreement,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
</style>