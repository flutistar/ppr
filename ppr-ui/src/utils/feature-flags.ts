import type { LDClient, LDFlagSet, LDOptions, LDUser } from 'launchdarkly-js-client-sdk';
import { initialize } from 'launchdarkly-js-client-sdk'

/**
 * Default feature flags in case LD env key is not defined (eg, local development).
 */
export const defaultFlagSet: LDFlagSet = {
  'financing-statement': false,
  'ppr-ui-enabled': true, // PPR Search -  default true: Should remove from codebase,
  'ppr-sa-notice-enabled': false, // PPR Security Act Notice
  'cla-enabled': false, // Enables the Commercial Lien Registration flows
  'bcregistry-ui-mhr-enabled': true,
  'search-registration-number': true,
  'search-serial-number': true,
  'mhr-ui-enabled': true, // Mhr Search - default true: Should remove from codebase
  'mhr-registration-enabled': false, // Enables MHR table tab
  'mhr-staff-correction-enabled': false, // Enables access to staff mhr correction
  'mhr-transfer-enabled': false, // Enables changes to base MHR HomeOwners within the MHR Information flow
  'mhr-misc-transfers-enabled': false, // Enables misc and non-bill sale transfers within the MHR Information flow
  'mhr-exemption-enabled': false,
  'mhr-non-res-exemption-enabled': false, // Enables Non-Residential Exemption for Staff
  'mhr-transport-permit-enabled': false,
  'mhr-amend-transport-permit-enabled': false,
  'mhr-cancel-transport-permit-enabled': false,
  'mhr-user-access-enabled': false,
  'mhr-history-enabled': false,
  'mhr-re-issue-permit-enabled': false, // Enables Create New and Extend Transport Permit: Staff Targeted for now
  'drs-integration-enabled': false, // Enables connections to Documents Record
  'mhr-enhanced-dealers-enabled': false, // Enables Dealer permissions for MHR Permits and Transfers
  'mhr-credit-card-enabled': false, // Enables credit card payment processing for MHR Products
  'sentry-enable': false, // by default, no sentry logs
  'banner-text': '' // by default, there is no banner text
}
/**
 * The Launch Darkly client instance.
 */
let ldClient: LDClient = null

/**
 * An async method that initializes the Launch Darkly client.
 */
export async function initLdClient (envKey: string): Promise<void> {
  if (envKey) {
    const user: LDUser = {
      // since we have no user data yet, use a shared key temporarily
      key: 'anonymous'
    }
    const options: LDOptions = {
      // fetch flags using REPORT request (to see user data as JSON)
      useReport: true,
      // opt out of sending diagnostics data
      diagnosticOptOut: true,
      // open streaming connection for live flag updates
      streaming: true
    }

    ldClient = initialize(envKey, user, options)

    try {
      await ldClient.waitForInitialization()
    } catch (e) {
      // shut down client -- `variation()` will return undefined values
      await ldClient.close()
      // NB: LD logs its own errors
    }
  }
}

/**
 * An async method that updates the Launch Darkly user properties.
 * @param key a unique string identifying a user
 * @param email the user's email address
 * @param firstName the user's first name
 * @param lastName the user's last name
 * @param custom optional object of additional attributes associated with the user
 */
export async function updateLdUser (
  key: string, email: string, firstName: string, lastName: string, custom: any = null
): Promise<void> {
  if (ldClient) {
    const user: LDUser = { key, email, firstName, lastName, custom }
    try {
      await ldClient.identify(user)
    } catch (e) {
      // NB: LD logs its own errors
    }
  }
}

/**
 * A method that gets the value of the specified feature flag.
 * @param name the name of the feature flag
 * @returns the flag value/variation, or undefined if the flag is not found
 */
export function getFeatureFlag (name: string): any {
  return ldClient ? ldClient.variation(name, defaultFlagSet[name]) : defaultFlagSet[name]
}

/**
 * Sets all boolean properties in the given default flag set object to true.
 * @param defaultValue - The default flag value.
 */
export function setAllFlagDefaults(defaultValue: boolean): void {
  for (const key in defaultFlagSet) {
    if (Object.prototype.hasOwnProperty.call(defaultFlagSet, key) && typeof defaultFlagSet[key] === 'boolean') {
      defaultFlagSet[key] = defaultValue
    }
  }
}
