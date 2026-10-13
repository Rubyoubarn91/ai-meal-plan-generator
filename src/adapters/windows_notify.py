"""Windows notification adapter. Uses PowerShell toast, no extra deps."""

from __future__ import annotations

import subprocess
import sys

_TOAST_TEMPLATE = """
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
$xml = $template.GetXml()
($xml = $xml -replace '<text id