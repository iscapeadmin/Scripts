# Work ideas: Harbourside Dental Group (DEMO)

Generated 21 Nov 2026 from hudu, halo, domotz. 31 ideas, about 107.3 technician hours in total.

| Priority | Ideas |
|---|---|
| P1 | 5 |
| P2 | 12 |
| P3 | 9 |
| P4 | 5 |

| # | Pri | Idea | Category | Effort | Billing | Due |
|---|---|---|---|---|---|---|
| 1 | P1 | Renew 2 SSL certificates (1 already expired) | Security | 1h | Agreement | 15 Nov 2026 |
| 2 | P1 | Investigate 1 infrastructure device showing offline in monitoring | Reliability | 1h | Agreement | 21 Nov 2026 |
| 3 | P1 | Remediate Windows 10 end of support on 6 devices | Lifecycle | 12h | Project / Quote | 21 Nov 2026 |
| 4 | P1 | Remediate Windows Server 2012 / 2012 R2 end of support on 1 device | Lifecycle | 16h | Project / Quote | 21 Nov 2026 |
| 5 | P1 | Review 2 infrastructure devices with expired warranty | Lifecycle | 1.5h | Project / Quote | 21 Nov 2026 |
| 6 | P2 | Remediate Windows 11 23H2 end of support on 4 devices | Lifecycle | 4h | Agreement | 21 Nov 2026 |
| 7 | P2 | Remediate Windows 11 24H2 end of support on 5 devices | Lifecycle | 5h | Agreement | 21 Nov 2026 |
| 8 | P2 | Renew support/security subscriptions on 1 device | Security | 0.5h | Project / Quote | 15 Dec 2026 |
| 9 | P2 | Warranty expiring within 90 days on 1 infrastructure device | Lifecycle | 1.2h | Project / Quote | 30 Dec 2026 |
| 10 | P2 | Renew 1 domain expiring within 60 days | Security | 0.5h | Agreement | 10 Jan 2027 |
| 11 | P2 | Plan for Windows Server 2016 end of support on 1 device | Lifecycle | 16h | Project / Quote | 12 Jan 2027 |
| 12 | P2 | Build a replacement plan for 1 storage device older than 6 years | Project Opportunity | 2h | Project / Quote |  |
| 13 | P2 | Build a replacement plan for 2 servers older than 6 years | Project Opportunity | 2h | Project / Quote |  |
| 14 | P2 | Fill documentation gaps: Backup, Network diagram, Internet circuit, UPS, Wireless | Documentation | 5h | Agreement |  |
| 15 | P2 | Root-cause project: Network & Wi-Fi (10 tickets in 90 days) | Service Improvement | 3h | Project / Quote |  |
| 16 | P2 | Root-cause project: Printing & scanning (10 tickets in 90 days) | Service Improvement | 2.5h | Agreement |  |
| 17 | P2 | Rotate 5 credentials not changed in over 12 months (4 privileged) | Security | 1.8h | Agreement |  |
| 18 | P3 | Build a replacement plan for 12 workstations older than 5 years | Project Opportunity | 2h | Project / Quote |  |
| 19 | P3 | Document 5 infrastructure devices found by monitoring but missing from Hudu | Documentation | 1.8h | Agreement |  |
| 20 | P3 | Investigate 2 devices with repeated tickets | Reliability | 3h | Agreement |  |
| 21 | P3 | Review 3 tickets open more than 30 days | Service Improvement | 0.8h | Internal |  |
| 22 | P3 | Roll out self-service password reset (10 lockout/password tickets in 90 days) | Service Improvement | 4h | Project / Quote |  |
| 23 | P3 | Root-cause project: Email & Outlook (7 tickets in 90 days) | Service Improvement | 2h | Agreement |  |
| 24 | P3 | Root-cause project: Performance (5 tickets in 90 days) | Service Improvement | 2h | Agreement |  |
| 25 | P3 | Root-cause project: Remote access & VPN (5 tickets in 90 days) | Service Improvement | 2h | Agreement |  |
| 26 | P3 | Standardise firmware across 2 device models running mixed versions | Security | 3.75h | Agreement |  |
| 27 | P4 | Review 13 devices with expired warranty | Lifecycle | 4.2h | Agreement | 21 Nov 2026 |
| 28 | P4 | Clean up 2 devices offline for 7+ days | Documentation | 0.7h | Agreement |  |
| 29 | P4 | Offer a 1:1 check-in or training for 4 high-ticket users | Service Improvement | 4h | Agreement |  |
| 30 | P4 | Complete missing asset details on 4 Hudu records | Documentation | 0.9h | Agreement |  |
| 31 | P4 | Review 5 KB articles not updated in 18+ months | Documentation | 1.2h | Internal |  |

## 1. [P1] Renew 2 SSL certificates (1 already expired)

*Security · impact 3/3 · urgency 3/3 · ~1h · Agreement · due 15 Nov 2026 · `security.expiring_certs_domains` · id `b130cc53e4a8`*

Renew and install the certificate, then check every place it is bound (firewall SSL-VPN, RD Gateway, web server, mail).

**Evidence**

- portal.harbourside-demo.com.au: 15 Nov 2026
- remote.harbourside-demo.com.au: 5 Dec 2026

## 2. [P1] Investigate 1 infrastructure device showing offline in monitoring

*Reliability · impact 3/3 · urgency 3/3 · ~1h · Agreement · due 21 Nov 2026 · `reliability.offline_devices` · id `7ec528af80a1`*

Find out whether each device is down, replaced or simply not polled. Fix it, or update the monitoring and documentation so the alerting can be trusted.

**Evidence**

- HSD-NAS01 (storage, 10.20.0.20): offline since 18 Nov 2026

## 3. [P1] Remediate Windows 10 end of support on 6 devices

*Lifecycle · impact 3/3 · urgency 3/3 · ~12h · Project / Quote · due 21 Nov 2026 · `lifecycle.os_eol` · id `d68970683fad`*

Vendor support for Windows 10 ended 14 Oct 2025. Devices that no longer get security patches are a cyber-insurance and Essential Eight gap. Upgrade in place to Windows 11 where the hardware supports it, otherwise replace. Confirm whether the client has paid for Extended Security Updates..

**Evidence**

- HSD-LT-RECEP-01: Microsoft Windows 10 Pro 22H2
- HSD-LT-SURG-02: Microsoft Windows 10 Pro 22H2
- HSD-PC-SURG-03: Microsoft Windows 10 Pro 22H2
- HSD-LT-SURG-04: Microsoft Windows 10 Pro 22H2
- HSD-LT-ACC-05: Microsoft Windows 10 Pro 22H2
- HSD-PC-ACC-06: Microsoft Windows 10 Pro 22H2

## 4. [P1] Remediate Windows Server 2012 / 2012 R2 end of support on 1 device

*Lifecycle · impact 3/3 · urgency 3/3 · ~16h · Project / Quote · due 21 Nov 2026 · `lifecycle.os_eol` · id `20ceb611a19b`*

Vendor support for Windows Server 2012 / 2012 R2 ended 10 Oct 2023. Devices that no longer get security patches are a cyber-insurance and Essential Eight gap. Migrate workloads to a supported server or the cloud, then decommission. Confirm whether ESUs (via Azure Arc) are in place..

**Evidence**

- HSD-APP01: Microsoft Windows Server 2012 R2 Standard

## 5. [P1] Review 2 infrastructure devices with expired warranty

*Lifecycle · impact 3/3 · urgency 3/3 · ~1.5h · Project / Quote · due 21 Nov 2026 · `lifecycle.warranty` · id `8a23a8a72544`*

Decide for each device whether to extend the warranty, replace it, or accept the risk. Put this in the client's next QBR or lifecycle report. These are infrastructure, so an unplanned hardware failure means a site-wide outage. Quote an extension or replacement.

**Evidence**

- HSD-NAS01 (storage, Synology DS918+): warranty 20 Sep 2021
- HSD-DC01 (server, Dell PowerEdge T330): warranty 12 Mar 2023

## 6. [P2] Remediate Windows 11 23H2 end of support on 4 devices

*Lifecycle · impact 2/3 · urgency 3/3 · ~4h · Agreement · due 21 Nov 2026 · `lifecycle.os_eol` · id `d9de628cdbd8`*

Vendor support for Windows 11 23H2 ended 11 Nov 2025. Devices that no longer get security patches are a cyber-insurance and Essential Eight gap. Push the current Windows 11 feature update.

**Evidence**

- HSD-LT-MGR-07: Microsoft Windows 11 Pro 23H2 (22631)
- HSD-LT-HYG-08: Microsoft Windows 11 Pro 23H2 (22631)
- HSD-PC-HYG-09: Microsoft Windows 11 Pro 23H2 (22631)
- HSD-LT-STER-10: Microsoft Windows 11 Pro 23H2 (22631)

## 7. [P2] Remediate Windows 11 24H2 end of support on 5 devices

*Lifecycle · impact 2/3 · urgency 3/3 · ~5h · Agreement · due 21 Nov 2026 · `lifecycle.os_eol` · id `55ea79896cf2`*

Vendor support for Windows 11 24H2 ended 13 Oct 2026. Devices that no longer get security patches are a cyber-insurance and Essential Eight gap. Push the current Windows 11 feature update.

**Evidence**

- HSD-LT-RECEP-11: Microsoft Windows 11 Pro 24H2 (26100)
- HSD-PC-SURG-12: Microsoft Windows 11 Pro 24H2 (26100)
- HSD-LT-HYG-13: Microsoft Windows 11 Pro 24H2 (26100)
- HSD-LT-ACC-14: Microsoft Windows 11 Pro 24H2 (26100)
- HSD-PC-MGR-15: Microsoft Windows 11 Pro 24H2 (26100)

## 8. [P2] Renew support/security subscriptions on 1 device

*Security · impact 3/3 · urgency 2/3 · ~0.5h · Project / Quote · due 15 Dec 2026 · `lifecycle.support_renewal` · id `0aa14ccbd9ec`*

Firewall and appliance subscriptions (IPS, web filtering, firmware access, vendor support) must stay current. Raise the renewal quote now so there is no gap in protection.

**Evidence**

- HSD-FW01: renewal 15 Dec 2026

## 9. [P2] Warranty expiring within 90 days on 1 infrastructure device

*Lifecycle · impact 3/3 · urgency 2/3 · ~1.2h · Project / Quote · due 30 Dec 2026 · `lifecycle.warranty` · id `756c94fcb691`*

Decide for each device whether to extend the warranty, replace it, or accept the risk. Put this in the client's next QBR or lifecycle report. These are infrastructure, so an unplanned hardware failure means a site-wide outage. Quote an extension or replacement.

**Evidence**

- HSD-HV01 (server, Dell PowerEdge R740): warranty 30 Dec 2026

## 10. [P2] Renew 1 domain expiring within 60 days

*Security · impact 3/3 · urgency 2/3 · ~0.5h · Agreement · due 10 Jan 2027 · `security.expiring_certs_domains` · id `4bafc3d89ca7`*

Renew the domain and set it to auto-renew. Confirm the registrar contact details are current and registrar lock is on.

**Evidence**

- harbourside-demo.com.au: 10 Jan 2027

## 11. [P2] Plan for Windows Server 2016 end of support on 1 device

*Lifecycle · impact 3/3 · urgency 2/3 · ~16h · Project / Quote · due 12 Jan 2027 · `lifecycle.os_eol` · id `06a09ba7ce60`*

Vendor support for Windows Server 2016 ends 12 Jan 2027 (52 days). Devices that no longer get security patches are a cyber-insurance and Essential Eight gap. Plan the migration to Windows Server 2025 or to the cloud. Quote it this quarter..

**Evidence**

- HSD-DC01: Microsoft Windows Server 2016 Standard

## 12. [P2] Build a replacement plan for 1 storage device older than 6 years

*Project Opportunity · impact 3/3 · urgency 2/3 · ~2h · Project / Quote · `lifecycle.hardware_age` · id `afdf6d7c25ec`*

These devices are past the 6-year replacement guideline. Bring a costed, staged refresh plan to the client so the spend can be budgeted rather than forced by failure.

**Evidence**

- HSD-NAS01: purchased 20 Sep 2018

## 13. [P2] Build a replacement plan for 2 servers older than 6 years

*Project Opportunity · impact 3/3 · urgency 2/3 · ~2h · Project / Quote · `lifecycle.hardware_age` · id `9c787479f2f8`*

These devices are past the 6-year replacement guideline. Bring a costed, staged refresh plan to the client so the spend can be budgeted rather than forced by failure.

**Evidence**

- HSD-DC01: purchased 12 Mar 2018
- HSD-HV01: purchased 2 Jun 2020

## 14. [P2] Fill documentation gaps: Backup, Network diagram, Internet circuit, UPS, Wireless

*Documentation · impact 3/3 · urgency 2/3 · ~5h · Agreement · `documentation.coverage_gaps` · id `1001332648b3`*

The client has no Hudu record for these standard items. Each gap usually means either the service isn't in place or the knowledge sits in one technician's head. A missing backup record is the most important. Confirm what is backed up, where to, how long it is kept, and when a restore was last tested.

**Evidence**

- No asset in layout(s) Backup, Backups, Datto
- No asset in layout(s) Network Diagrams
- No asset in layout(s) internet circuit
- No asset in layout(s) UPS
- No asset in layout(s) Wireless

## 15. [P2] Root-cause project: Network & Wi-Fi (10 tickets in 90 days)

*Service Improvement · impact 3/3 · urgency 2/3 · ~3h · Project / Quote · `tickets.recurring_theme` · id `496ac177936d`*

Network & Wi-Fi made up 23% of tickets in the last 90 days, about 10 hours of reactive time. Run a wireless survey and network health check (AP placement, channel plan, switch errors, ISP SLA). Quote any upgrade it shows is needed.

**Evidence**

- #18270 12 Nov 2026: VPN disconnecting when working from home
- #18404 8 Nov 2026: Wifi dropping in surgery 2
- #18395 7 Nov 2026: Wifi dropping in surgery 2
- #18394 31 Oct 2026: Wifi dropping in surgery 2
- #18406 25 Oct 2026: Wifi dropping in surgery 2
- #18411 7 Oct 2026: Wifi dropping in surgery 2
- #18298 6 Oct 2026: VPN disconnecting when working from home
- #18283 30 Aug 2026: VPN disconnecting when working from home
- #18278 27 Aug 2026: VPN disconnecting when working from home
- #18290 27 Aug 2026: VPN disconnecting when working from home

## 16. [P2] Root-cause project: Printing & scanning (10 tickets in 90 days)

*Service Improvement · impact 3/3 · urgency 2/3 · ~2.5h · Agreement · `tickets.recurring_theme` · id `5ea1cfdd12f5`*

Printing & scanning made up 23% of tickets in the last 90 days, about 8.25 hours of reactive time. Standardise printer deployment (Universal Print or a GPO/Intune print policy), update drivers, and check whether the fleet or managed-print contract needs review.

**Evidence**

- #18247 15 Nov 2026: Scan to email not working on Brother MFC
- #18226 10 Nov 2026: Printer at reception not printing
- #18234 5 Nov 2026: Printer at reception not printing
- #18240 1 Nov 2026: Printer at reception not printing
- #18222 20 Oct 2026: Printer at reception not printing
- #18209 27 Sep 2026: Printer at reception not printing
- #18232 24 Sep 2026: Printer at reception not printing
- #18256 8 Sep 2026: Scan to email not working on Brother MFC
- #18217 7 Sep 2026: Printer at reception not printing
- #18262 5 Sep 2026: Scan to email not working on Brother MFC

## 17. [P2] Rotate 5 credentials not changed in over 12 months (4 privileged)

*Security · impact 3/3 · urgency 2/3 · ~1.8h · Agreement · `security.stale_credentials` · id `9415b19b1e63`*

Rotate these passwords and update the vault. Start with privileged, shared and service accounts. For any account that turns out to be unused, disable it instead of rotating it. Where possible, move service accounts to managed identities or gMSAs.

**Evidence**

- Domain Administrator: last changed 1 May 2023
- FortiGate admin: last changed 1 Feb 2024
- Synology NAS admin: last changed 9 Sep 2021
- svc-backup: last changed 14 Feb 2022
- Wi-Fi PSK - Staff: last changed 1 Aug 2022

## 18. [P3] Build a replacement plan for 12 workstations older than 5 years

*Project Opportunity · impact 2/3 · urgency 2/3 · ~2h · Project / Quote · `lifecycle.hardware_age` · id `8d051e2d3f7e`*

These devices are past the 5-year replacement guideline. Bring a costed, staged refresh plan to the client so the spend can be budgeted rather than forced by failure.

**Evidence**

- HSD-PC-SURG-12: purchased 13 Jan 2019
- HSD-LT-SURG-02: purchased 3 Mar 2019
- HSD-LT-SURG-04: purchased 5 May 2019
- HSD-PC-ACC-06: purchased 7 Jul 2019
- HSD-PC-RECEP-18: purchased 19 Jul 2019
- HSD-LT-RECEP-01: purchased 2 Feb 2020
- HSD-LT-HYG-13: purchased 14 Feb 2020
- HSD-PC-SURG-03: purchased 4 Apr 2020
- HSD-LT-ACC-05: purchased 6 Jun 2020
- HSD-LT-MGR-07: purchased 8 Aug 2020
- HSD-LT-ACC-14: purchased 15 Mar 2021
- HSD-LT-HYG-08: purchased 9 Sep 2021

## 19. [P3] Document 5 infrastructure devices found by monitoring but missing from Hudu

*Documentation · impact 2/3 · urgency 2/3 · ~1.8h · Agreement · `documentation.undocumented_devices` · id `c29039ae75e6`*

Create Hudu assets for these devices with management IP, credentials, firmware, warranty and location. Undocumented infrastructure slows down every incident that involves it.

**Evidence**

- HSD-SW02 (network, Aruba 2930F-24G, 10.20.0.3)
- AP-Reception (network, Ubiquiti U6-Pro, 10.20.0.31)
- AP-Surgery (network, Ubiquiti U6-Pro, 10.20.0.32)
- AP-Staffroom (network, Ubiquiti U6-Pro, 10.20.0.33)
- PRN-Reception (printer, Brother MFC-L8900CDW, 10.20.0.50)

## 20. [P3] Investigate 2 devices with repeated tickets

*Reliability · impact 2/3 · urgency 2/3 · ~3h · Agreement · `tickets.repeat_offenders` · id `6e4a8fbd0100`*

These devices keep coming back. Do a full health check (hardware diagnostics, event logs, reimage if needed). If they are old or out of warranty, recommend replacement.

**Evidence**

- PRN-Reception: 7 tickets (Scan to email not working on Brother MFC; Printer at reception not printing; Printer at reception not printing)
- HSD-LT-ACC-05: 3 tickets (PC very slow in the morning; PC very slow in the morning; PC very slow in the morning)

## 21. [P3] Review 3 tickets open more than 30 days

*Service Improvement · impact 2/3 · urgency 2/3 · ~0.8h · Internal · `tickets.aged_open` · id `3e5d3e41b1e3`*

Close, escalate or convert each one to a project. Long-open tickets hurt client satisfaction and often hide a bigger issue.

**Evidence**

- #18468 opened 1 Aug 2026: Migrate practice software DB to new server - scoping
- #18462 opened 18 Sep 2026: Quote for second monitor - Dr Chen
- #18465 opened 7 Oct 2026: Intermittent BSOD on HSD-PC-SURG-03

## 22. [P3] Roll out self-service password reset (10 lockout/password tickets in 90 days)

*Service Improvement · impact 2/3 · urgency 2/3 · ~4h · Project / Quote · `tickets.password_resets` · id `477a52908933`*

Turn on Entra ID SSPR with password writeback and combined MFA/SSPR registration. Run a short enrolment campaign, and consider passkeys or Windows Hello for Business to cut password use entirely.

**Evidence**

- #18306 13 Nov 2026: Password reset - locked out
- #18317 10 Nov 2026: Password reset - locked out
- #18385 7 Nov 2026: Outlook keeps asking for password
- #18369 4 Nov 2026: Outlook keeps asking for password
- #18386 27 Oct 2026: Outlook keeps asking for password
- #18309 20 Oct 2026: Password reset - locked out
- #18378 1 Oct 2026: Outlook keeps asking for password
- #18324 11 Sep 2026: Password reset - locked out
- #18331 11 Sep 2026: Password reset - locked out
- #18337 25 Aug 2026: Password reset - locked out

## 23. [P3] Root-cause project: Email & Outlook (7 tickets in 90 days)

*Service Improvement · impact 2/3 · urgency 2/3 · ~2h · Agreement · `tickets.recurring_theme` · id `9acdeb046e52`*

Email & Outlook made up 16% of tickets in the last 90 days, about 5 hours of reactive time. Review mailbox sizes and archiving, Outlook profile and add-in health, and shared mailbox permissions. Consider New Outlook readiness and a short user tip sheet.

**Evidence**

- #18247 15 Nov 2026: Scan to email not working on Brother MFC
- #18385 7 Nov 2026: Outlook keeps asking for password
- #18369 4 Nov 2026: Outlook keeps asking for password
- #18386 27 Oct 2026: Outlook keeps asking for password
- #18378 1 Oct 2026: Outlook keeps asking for password
- #18256 8 Sep 2026: Scan to email not working on Brother MFC
- #18262 5 Sep 2026: Scan to email not working on Brother MFC

## 24. [P3] Root-cause project: Performance (5 tickets in 90 days)

*Service Improvement · impact 2/3 · urgency 2/3 · ~2h · Agreement · `tickets.recurring_theme` · id `186490720aa3`*

Performance made up 11% of tickets in the last 90 days, about 5 hours of reactive time. Correlate the slow devices with hardware age, disk and RAM, and startup bloat. Clean up at scale with RMM scripts and add any machine below spec to the refresh plan.

**Evidence**

- #18340 10 Nov 2026: PC very slow in the morning
- #18343 22 Oct 2026: PC very slow in the morning
- #18356 15 Oct 2026: PC very slow in the morning
- #18363 13 Sep 2026: PC very slow in the morning
- #18351 6 Sep 2026: PC very slow in the morning

## 25. [P3] Root-cause project: Remote access & VPN (5 tickets in 90 days)

*Service Improvement · impact 2/3 · urgency 2/3 · ~2h · Agreement · `tickets.recurring_theme` · id `c85a4cb889bb`*

Remote access & VPN made up 11% of tickets in the last 90 days, about 5 hours of reactive time. Review the remote access design: VPN client versions, MFA, split tunnelling, and whether it can move to ZTNA or cloud-hosted apps.

**Evidence**

- #18270 12 Nov 2026: VPN disconnecting when working from home
- #18298 6 Oct 2026: VPN disconnecting when working from home
- #18283 30 Aug 2026: VPN disconnecting when working from home
- #18278 27 Aug 2026: VPN disconnecting when working from home
- #18290 27 Aug 2026: VPN disconnecting when working from home

## 26. [P3] Standardise firmware across 2 device models running mixed versions

*Security · impact 2/3 · urgency 2/3 · ~3.75h · Agreement · `reliability.firmware_drift` · id `cb9eaddf5fb3`*

The same model is running different firmware versions. Check the vendor advisories, then bring every unit up to the current recommended release in a maintenance window.

**Evidence**

- Aruba 2930F-24G: HSD-SW01=WC.16.11.0016, HSD-SW02=WC.16.10.0012
- Ubiquiti U6-Pro: AP-Reception=6.6.77, AP-Staffroom=6.5.62, AP-Surgery=6.6.77

## 27. [P4] Review 13 devices with expired warranty

*Lifecycle · impact 1/3 · urgency 2/3 · ~4.2h · Agreement · due 21 Nov 2026 · `lifecycle.warranty` · id `79ac509fe7b7`*

Decide for each device whether to extend the warranty, replace it, or accept the risk. Put this in the client's next QBR or lifecycle report.

**Evidence**

- HSD-PC-SURG-12 (workstation, Dell Latitude 5420): warranty 12 Jan 2022
- HSD-LT-SURG-02 (workstation, HP Latitude 5420): warranty 2 Mar 2022
- HSD-LT-SURG-04 (workstation, HP Latitude 5420): warranty 4 May 2022
- HSD-PC-ACC-06 (workstation, Dell OptiPlex 7090): warranty 6 Jul 2022
- HSD-PC-RECEP-18 (workstation, Dell ThinkPad T14): warranty 18 Jul 2022
- HSD-LT-RECEP-01 (workstation, Lenovo ThinkPad T14): warranty 1 Feb 2023
- HSD-LT-HYG-13 (workstation, Dell EliteBook 840 G8): warranty 13 Feb 2023
- HSD-PC-SURG-03 (workstation, HP Latitude 5420): warranty 4 Apr 2023
- HSD-LT-MGR-07 (workstation, Dell ThinkPad T14): warranty 8 Aug 2023
- HSD-LT-ACC-14 (workstation, Dell Latitude 5420): warranty 14 Mar 2024
- HSD-LT-HYG-08 (workstation, HP OptiPlex 7090): warranty 8 Sep 2024
- HSD-PC-HYG-09 (workstation, HP Latitude 5420): warranty 9 Oct 2025
- HSD-LT-SURG-16 (workstation, Dell ThinkPad T14): warranty 16 May 2026

## 28. [P4] Clean up 2 devices offline for 7+ days

*Documentation · impact 1/3 · urgency 2/3 · ~0.7h · Agreement · `reliability.offline_devices` · id `58a558514a6d`*

These devices haven't been seen for a while. Confirm with the client whether they're retired, then remove them from monitoring and archive them in documentation, so asset counts and billing stay accurate.

**Evidence**

- iPhone-front-desk: last seen 30 Sep 2026
- Galaxy-Tab-01: last seen 2 Oct 2026

## 29. [P4] Offer a 1:1 check-in or training for 4 high-ticket users

*Service Improvement · impact 1/3 · urgency 2/3 · ~4h · Agreement · `tickets.repeat_offenders` · id `6edfb785f956`*

A short desk-side session often uncovers a bad device, a missing permission or a workflow gap behind a run of tickets. This is a good account-management touchpoint.

**Evidence**

- Sarah Nguyen: 13 tickets
- Emma Wilson: 7 tickets
- Tom Bennett: 5 tickets
- Dr Michael Chen: 5 tickets

## 30. [P4] Complete missing asset details on 4 Hudu records

*Documentation · impact 1/3 · urgency 1/3 · ~0.9h · Agreement · `documentation.incomplete_records` · id `ac4b3f7a1175`*

Fill in serials, warranty dates and OS versions. Use the RMM/Hudu integration sync or the vendor warranty lookup where possible. Lifecycle and warranty reporting is only as good as these fields.

**Evidence**

- HSD-APP01: missing serial, warranty date
- HSD-LT-ACC-05: missing serial, warranty date
- HSD-LT-STER-10: missing serial, warranty date
- HSD-PC-MGR-15: missing serial, warranty date

## 31. [P4] Review 5 KB articles not updated in 18+ months

*Documentation · impact 1/3 · urgency 1/3 · ~1.2h · Internal · `documentation.stale_articles` · id `f14e4ed76235`*

Check each article against the live environment. Update it, merge it into another, or archive it. Out-of-date procedures cause failed fixes and wrong escalations.

**Evidence**

- Server reboot order: last updated 19 Jul 2021
- Printer setup: last updated 14 Mar 2022
- Backup restore procedure: last updated 30 Nov 2022
- VPN client install: last updated 9 Jan 2023
- Imaging software restart procedure: last updated 2 Feb 2024

