import argparse
import os
import library.localstore as store
import library.status.alertstatus as askeys
import library.migrationlogger as m_logger
import library.clients.alertsclient as ac
import library.utils as utils
import fetchchannels

# Migrates alert policy and assigned notification channels to targetAccount
# Alert Policy and Notification Channels are created only if not present in the targetAccount

log = m_logger.get_logger(os.path.basename(__file__))


def configure_parser():
    parser = argparse.ArgumentParser(description='Store Alert Policies and channels')
    parser.add_argument('--sourceAccount', nargs=1, type=str, required=True, help='Source accountId')
    parser.add_argument('--sourceApiKey', nargs=1, type=str, required=True, help='Source account API Key or \
                                                                        set environment variable ENV_SOURCE_API_KEY')
    parser.add_argument('--sourceRegion', type=str, nargs=1, required=False, help='sourceRegion us(default) or eu')
    return parser


def print_args(args, src_api_key, src_region):
    log.info("Using sourceAccount : " + str(args.sourceAccount[0]))
    log.info("Using sourceApiKey : " + len(src_api_key[:-4])*"*" + src_api_key[-4:])
    log.info("sourceRegion : " + src_region)


def store_alert_policies(src_account, src_api_key, src_region):
    log.info('Starting store alert policies.')
    policies = ac.get_all_alert_policies(src_api_key, src_region)
    store.save_alert_policies(src_account, policies)
    policy_file_name = str(src_account)+'_policies.csv'
    policy_names_file = store.create_output_file(policy_file_name)
    with policy_names_file.open('a') as policy_names_out:
        for policy in policies['policies']:
            policy_name = policy['name']
            # policy_name = store.sanitize(policy_name)
            policy_names_out.write(policy_name + "\n")
        policy_names_out.close()
    log.info("Policy names stored in " + policy_file_name)
    log.info("Policies JSON stored in " + "db/"+str(src_account)+"/alert_policies/alert_policies.json")
    log.info('Finished store alert policies.')


def main():
    parser = configure_parser()
    args = parser.parse_args()
    src_api_key = utils.ensure_source_api_key(args)
    src_region = utils.ensure_source_region(args)
    if not src_api_key:
        utils.error_and_exit('source_api_key', 'ENV_SOURCE_API_KEY')
    store_alert_policies(args.sourceAccount[0], src_api_key, src_region)


if __name__ == '__main__':
    main()
