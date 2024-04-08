# Copyright 2023-2024. WebPros International GmbH. All rights reserved.

import os
import shutil

from pleskdistup.common import action, systemd

OS_VENDOR_PHP_FPM_CONFIG = "/etc/php-fpm.d/www.conf"


class FixOsVendorPhpFpmConfiguration(action.ActiveAction):
    def __init__(self):
        self.name = "fix OS vendor PHP configuration"

    def is_required(self) -> bool:
        if os.path.exists(OS_VENDOR_PHP_FPM_CONFIG):
            return True

    def _prepare_action(self) -> action.ActionResult:
        return action.ActionResult()

    def _post_action(self) -> action.ActionResult:
        # Plesk expect www pool to be disabled by default.
        # Every distro should has the same configuration generated by Plesk.
        # However we store the original configuration in the www.conf.saved_by_psa file.
        if os.path.exists(f"{OS_VENDOR_PHP_FPM_CONFIG}.rpmnew"):
            shutil.move(f"{OS_VENDOR_PHP_FPM_CONFIG}.rpmnew", f"{OS_VENDOR_PHP_FPM_CONFIG}.saved_by_psa")
        elif os.path.exists(f"{OS_VENDOR_PHP_FPM_CONFIG}.rpmsave"):
            shutil.move(f"{OS_VENDOR_PHP_FPM_CONFIG}", f"{OS_VENDOR_PHP_FPM_CONFIG}.saved_by_psa")
            shutil.move(f"{OS_VENDOR_PHP_FPM_CONFIG}.rpmsave", f"{OS_VENDOR_PHP_FPM_CONFIG}")

        if systemd.is_service_exists("php-fpm") and systemd.is_service_active("php-fpm"):
            systemd.restart_services(["php-fpm"])

        return action.ActionResult()

    def _revert_action(self) -> action.ActionResult:
        return action.ActionResult()

    def estimate_post_time(self):
        return 1
