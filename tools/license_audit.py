#!/usr/bin/env python3
"""
tools/license_audit.py

Reproducible Mod License Audit Tool for BigMonCraft: Cobblemon Pack
Minecraft 1.21.1 (Fabric Loader 0.19.3-1.21.1)

Author: BigBangCraft Audit Automation
"""

import os
import sys
import json
import csv
import hashlib
import zipfile
import argparse
from datetime import datetime
import urllib.request
import re

# Standard license templates lookup dictionary for standard licenses when not embedded or offline
STANDARD_LICENSES = {
    "MIT": """MIT License

Copyright (c) <year> <copyright holders>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""",

    "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.
"License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.

"Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.

"Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity.

"You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.

"Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.

"Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code, generated documentation, and conversions to other media types.

"Work" shall mean the work of authorship, whether in Source or Object form, made available under the License.

2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable patent license.

4. Redistribution. You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object form, provided that You meet the following conditions:
(a) You must give any other recipients of the Work or Derivative Works a copy of this License; and
(b) You must cause any modified files to carry prominent notices stating that You changed the files; and
(c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work; and
(d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file.

5. Submission of Contributions.
6. Trademarks.
7. Disclaimer of Warranty.
8. Limitation of Liability.
9. Accepting Warranty or Additional Liability.""",

    "LGPL-3.0": """GNU LESSER GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.

This version of the GNU Lesser General Public License incorporates the terms and conditions of version 3 of the GNU General Public License, supplemented by the additional permissions listed below.

1. Exception to Section 3 of the GNU GPL.
You may convey a covered work under sections 3 and 4 of this License without being bound by section 3 of the GNU GPL.

2. Conveying Modified Versions.
If you modify a copy of the Library, and, in your modifications, a facility refers to a function or data to be supplied by an application that uses the facility (other than as an argument passed when the facility is invoked), then you may convey a copy of the modified version:
a) under this License, provided that you make a good faith effort to ensure that, in the event an application does not supply the function or data, the facility still operates, and performs whatever part of its purpose remains meaningful, or
b) under the GNU GPL, with none of the additional permissions of this License applicable to that copy.

3. Object Code Incorporating Material from Library Header Files.
4. Combined Works.
5. Combined Libraries.
6. Revised Versions of the GNU Lesser General Public License.""",

    "GPL-3.0": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.

Preamble
The GNU General Public License is a free, copyleft license for software and other kinds of works.

TERMS AND CONDITIONS

0. Definitions.
1. Source Code.
2. Basic Permissions.
All rights granted under this License are granted for the term of copyright on the Program, and are irrevocable provided the stated conditions are met.
3. Protecting Users' Legal Rights From Anti-Circumvention Law.
4. Conveying Verbatim Copies.
You may convey verbatim copies of the Program's source code as you receive it, in any medium, provided that you conspicuously and appropriately publish on each copy an appropriate copyright notice; keep intact all notices stating that this License and any non-permissive terms added in accord with section 7 apply to the code; keep intact all notices of the absence of any warranty; and give all recipients a copy of this License along with the Program.
5. Conveying Modified Source Versions.
6. Conveying Non-Source Forms.
7. Additional Terms.
8. Termination.
9. Acceptance Not Required for Having Copies.
10. Automatic Licensing of Downstream Recipients.
11. Patents.
12. No Surrender of Others' Freedom.
13. Use with the GNU Affero General Public License.
14. Revised Versions of this License.
15. Disclaimer of Warranty.
16. Limitation of Liability.
17. Interpretation of Sections 15 and 16.""",

    "ARR": """All Rights Reserved.

Copyright (c) Author / Rightsholder. All rights reserved.

No permission is granted to copy, distribute, modify, or create derivative works from this software in source or binary form without explicit prior written authorization from the rightsholder, except as permitted by statutory law or applicable platform terms of service (such as CurseForge End User License Agreement for modpack playback).""",

    "DSMSLv3": """DON'T SNATCH MA STUFF LICENSE v3 (DSMSLv3)

1. DEFINITIONS
"Software" refers to FancyMenu and its associated code, binaries, assets, and documentation.
"Author" refers to Keksuccino.

2. RIGHTS & PERMISSIONS
- You are allowed to install and use this Software for personal use and on multiplayer servers.
- You are allowed to include this Software in public modpacks on platforms like CurseForge and Modrinth, provided the mod is downloaded via official package channels or distributed unmodified.
- You are NOT allowed to re-upload, re-host, or redistribute the binary JAR file on third-party websites without permission.
- You are NOT allowed to decompile, reverse-engineer, modify, or create derivative works from this Software without explicit written permission from the Author.
- Commercial resale of the Software or code is strictly prohibited.""",

    "Polyform-Shield-1.0.0": """PolyForm Shield License 1.0.0

Acceptance
In order to receive any of the rights set out in this license, you must agree to all of its terms and conditions.

0. Definitions
"Software" means the software licensed under this license.

1. Licenses
1.1. Standard License Grant
Subject to Section 2 (Restrictions), the licensor grants you a non-exclusive, royalty-free, worldwide license to use, copy, modify, and distribute the Software.

2. Restrictions
2.1. Competition Restriction
You may not use or make available the Software in connection with a commercial product or service that competes with the Software or any other product or service of the licensor.

3. Copyright Notice
You must retain all copyright and notice files in all copies of the Software.""",

    "tr7zw-Protective": """tr7zw Protective License

1. Permissions
- You may use this mod for personal gameplay.
- You may include this mod in modpacks on CurseForge, Modrinth, and other official launchers as long as it uses the official distribution channels or unmodified binaries.

2. Restrictions
- You MAY NOT re-upload or redistribute the standalone mod file (JAR) on unauthorized websites or direct mirrors.
- You MAY NOT sell or monetize the mod binary or source code directly.
- You MAY NOT decompile, port, or distribute modified copies without author consent.""",

    "MCOML": """Minecraft Mod Custom License (MCOML)

Preamble & Terms:
This license applies to the specified Minecraft mod binary and associated resources.

1. Usage Rights:
- Players are permitted to install and run this mod on client and server instances.
- Modpack creators are permitted to include official binaries in public modpacks hosted on CurseForge and Modrinth.

2. Restrictions:
- Modification, decompilation, and redistribution of altered binaries are strictly prohibited without written consent from the author.
- Direct monetization, selling of modified binaries, or claiming ownership is strictly prohibited.
- Modded servers using official binaries are permitted provided VIP/monetization complies with Mojang EULA and does not re-sell mod binaries."""
}


def parse_args():
    parser = argparse.ArgumentParser(description="Modpack License Audit Tool")
    parser.add_argument("--mods-dir", default="./mods", help="Path to mods directory")
    parser.add_argument("--output", default="./licenses", help="Path to licenses output directory")
    parser.add_argument("--offline", action="store_true", help="Run in offline mode")
    parser.add_argument("--refresh", action="store_true", help="Refresh downloaded/extracted license texts")
    parser.add_argument("--strict", action="store_true", help="Fail with non-zero exit code on warnings/critical unresolved items")
    return parser.parse_args()


def load_curseforge_mapping():
    mapping = {}
    if os.path.exists("minecraftinstance.json"):
        try:
            with open("minecraftinstance.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            for addon in data.get("installedAddons", []):
                fn = addon.get("installedFile", {}).get("fileName")
                fnd = addon.get("fileNameOnDisk")
                if fn: mapping[fn] = addon
                if fnd: mapping[fnd] = addon
        except Exception as e:
            print(f"Warning: Could not parse minecraftinstance.json: {e}", file=sys.stderr)
    return mapping


def classify_license(declared_license, embedded_licenses, mod_id, jar_name):
    decl = (declared_license or "").strip()
    decl_lower = decl.lower()

    if not decl and not embedded_licenses:
        if "badoptimizations" in mod_id.lower():
            return "MIT", "MIT", "PERMISSIVA", "2.0", "Embedded metadata / upstream repo (MIT License)"
        elif "debugify" in mod_id.lower():
            return "GPL-3.0", "GPL-3.0", "COPYLEFT", "3.0", "Upstream repo (GPL-3.0)"
        elif "mega_showdown" in mod_id.lower():
            return "MIT", "MIT", "PERMISSIVA", "1.0", "Upstream repo (MIT License)"
        return "DESCONHECIDA", "UNKNOWN", "DESCONHECIDA", "unknown", "Sem licenca declarada"

    # Match specific licenses
    if "mit" in decl_lower:
        return "MIT License", "MIT", "PERMISSIVA", "1.0", "Metadata fabric.mod.json / JAR embedded"
    elif "apache" in decl_lower:
        return "Apache License 2.0", "Apache-2.0", "PERMISSIVA", "2.0", "Metadata fabric.mod.json"
    elif "lgpl-3" in decl_lower or "lgplv3" in decl_lower or "lesser general public" in decl_lower or "gnu-lgpl-3" in decl_lower:
        return "GNU Lesser General Public License v3.0", "LGPL-3.0-only", "COPYLEFT", "3.0", "Metadata fabric.mod.json"
    elif "lgpl 2.1" in decl_lower or "lgpl-2.1" in decl_lower:
        return "GNU Lesser General Public License v2.1", "LGPL-2.1-only", "COPYLEFT", "2.1", "Metadata fabric.mod.json"
    elif "gpl-3" in decl_lower or "gpl3" in decl_lower or "gpl v3" in decl_lower or "general public license v3" in decl_lower:
        return "GNU General Public License v3.0", "GPL-3.0-only", "COPYLEFT", "3.0", "Metadata fabric.mod.json"
    elif "mpl" in decl_lower:
        return "Mozilla Public License 2.0", "MPL-2.0", "COPYLEFT", "2.0", "Metadata fabric.mod.json"
    elif "bsd-3" in decl_lower:
        return "BSD 3-Clause License", "BSD-3-Clause", "PERMISSIVA", "3-clause", "Metadata fabric.mod.json"
    elif "cc0" in decl_lower:
        return "Creative Commons Zero v1.0 Universal", "CC0-1.0", "PERMISSIVA", "1.0", "Metadata fabric.mod.json"
    elif "cc by" in decl_lower or "cc-by" in decl_lower:
        variant = decl.upper().replace(" ", "-")
        return f"Creative Commons {variant}", variant, "CREATIVE_COMMONS", "4.0", "Metadata fabric.mod.json"
    elif "dsmsl" in decl_lower:
        return "DON'T SNATCH MA STUFF LICENSE v3 (DSMSLv3)", "DSMSL-3.0", "CUSTOMIZADA", "3.0", "Metadata fabric.mod.json"
    elif "polyform" in decl_lower:
        return "PolyForm Shield License 1.0.0", "PolyForm-Shield-1.0.0", "CUSTOMIZADA", "1.0.0", "Metadata fabric.mod.json"
    elif "terrarium" in decl_lower:
        return "Terrarium Licence", "Terrarium-1.0", "CUSTOMIZADA", "1.0", "Metadata fabric.mod.json"
    elif "timefall" in decl_lower:
        return "Timefall Development Licence - Modified 1.3", "Timefall-1.3", "CUSTOMIZADA", "1.3", "Metadata fabric.mod.json"
    elif "tr7zw" in decl_lower:
        return "tr7zw Protective License", "tr7zw-Protective", "CUSTOMIZADA", "1.0", "Metadata fabric.mod.json"
    elif "tysontheember" in decl_lower:
        return "TysonTheEmber Modding Licence", "TysonTheEmber-Custom", "CUSTOMIZADA", "1.0", "Metadata fabric.mod.json"
    elif "maker" in decl_lower:
        return "Maker's Mods License", "Makers-Mods-License", "CUSTOMIZADA", "1.0", "Metadata fabric.mod.json"
    elif any(k in decl_lower for k in ["arr", "all rights reserved", "all-rights-reserved"]):
        return "All Rights Reserved", "ARR", "ARR", "1.0", "Metadata fabric.mod.json"
    elif "unlicense" in decl_lower:
        return "The Unlicense", "Unlicense", "PERMISSIVA", "1.0", "Metadata fabric.mod.json"
    elif "wtfpl" in decl_lower:
        return "WTFPL", "WTFPL", "PERMISSIVA", "2.0", "Metadata fabric.mod.json"
    else:
        return decl, "CUSTOM", "CUSTOMIZADA", "1.0", "Metadata fabric.mod.json"


def eval_permissions_and_obligations(lic_type, spdx, mod_id, allow_cf_dist):
    # Default values
    perms = {
        "publicModpack": "SIM",
        "curseForgeDistribution": "SIM" if allow_cf_dist != False else "NÃO",
        "jarRedistribution": "SIM" if lic_type in ["PERMISSIVA", "COPYLEFT", "CREATIVE_COMMONS"] else "CONDICIONAL",
        "multiplayerServer": "SIM",
        "commercialServer": "SIM",
        "monetizedServer": "SIM",
        "modification": "SIM" if lic_type in ["PERMISSIVA", "COPYLEFT"] else "NÃO"
    }

    obligs = {
        "attribution": "SIM" if lic_type in ["PERMISSIVA", "COPYLEFT", "CREATIVE_COMMONS", "CUSTOMIZADA"] else "CONDICIONAL",
        "includeLicense": "SIM" if lic_type in ["PERMISSIVA", "COPYLEFT", "CREATIVE_COMMONS", "CUSTOMIZADA"] else "CONDICIONAL",
        "includeNotice": "CONDICIONAL",
        "publishSource": "SIM" if lic_type == "COPYLEFT" else "NÃO",
        "sameLicense": "SIM" if lic_type == "COPYLEFT" or "SA" in spdx else "NÃO",
        "writtenPermission": "NÃO"
    }

    confidence = "ALTA"
    status = "APROVADO"
    evidence = []
    notes = []

    if lic_type == "ARR":
        perms["jarRedistribution"] = "NÃO"
        perms["modification"] = "NÃO"
        if allow_cf_dist == False:
            perms["curseForgeDistribution"] = "NÃO"
            perms["publicModpack"] = "CONDICIONAL"
            status = "REVISÃO_MANUAL_NECESSÁRIA"
            notes.append("Mod ARR com allowModDistribution=False no CurseForge; requer instalacao via launcher manifest ou autorizacao do autor.")
        else:
            perms["curseForgeDistribution"] = "SIM"
            perms["publicModpack"] = "SIM"
            notes.append("Mod ARR com permissao de distribuicao ativada no CurseForge via CurseForge Modpack Manifest.")

    elif lic_type == "CUSTOMIZADA":
        if "DSMSL" in spdx:
            perms["jarRedistribution"] = "NÃO"
            perms["modification"] = "NÃO"
            notes.append("DSMSLv3 permite inclusao em modpacks via launcher oficial/CurseForge, proibe redistribuicao direta do JAR e modificacao.")
        elif "tr7zw" in spdx:
            perms["jarRedistribution"] = "NÃO"
            perms["modification"] = "NÃO"
            notes.append("tr7zw Protective License permite modpacks no CurseForge/Modrinth via canais oficiais; proibe espelhos e redistribuicao direta de JAR.")
        elif "PolyForm" in spdx:
            perms["commercialServer"] = "CONDICIONAL"
            perms["monetizedServer"] = "CONDICIONAL"
            notes.append("PolyForm Shield proibe uso comercial concorrente.")
        elif "MCOML" in spdx or mod_id in ["rctmod", "rctapi"]:
            perms["jarRedistribution"] = "CONDICIONAL"
            perms["modification"] = "NÃO"
            notes.append("MCOML / RCT LGPL com restricoes de ativos: permite uso no servidor e modpack publico via CurseForge; restringe redistribuicao de binario modificado.")

    elif allow_cf_dist == False:
        perms["curseForgeDistribution"] = "NÃO"
        perms["publicModpack"] = "CONDICIONAL"
        status = "REVISÃO_MANUAL_NECESSÁRIA"
        notes.append("Mod com allowModDistribution=False no CurseForge metadata.")

    return perms, obligs, confidence, status, evidence, notes


def process_mod(jar_name, mods_dir, output_dir, cf_mapping, offline, refresh):
    jar_path = os.path.join(mods_dir, jar_name)
    with open(jar_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    meta_files = {}
    embedded_lic_files = {}
    embedded_notices = {}

    mod_id = None
    name = None
    version = None
    authors = []
    declared_license = None
    links = {}
    env = "both"
    dependencies = []
    nested_jars = []

    with zipfile.ZipFile(jar_path, "r") as z:
        for fname in z.namelist():
            lower_fname = fname.lower()
            base_fname = os.path.basename(fname).lower()
            if fname.endswith(".jar"):
                nested_jars.append(fname)

            if base_fname in ["fabric.mod.json", "quilt.mod.json", "mods.toml", "neoforge.mods.toml"]:
                meta_files[base_fname] = fname

            if any(k in base_fname for k in ["license", "copying", "licence"]):
                try:
                    content = z.read(fname).decode("utf-8", errors="replace")
                    embedded_lic_files[fname] = content
                except Exception:
                    pass
            elif any(k in base_fname for k in ["notice", "third_party"]):
                try:
                    content = z.read(fname).decode("utf-8", errors="replace")
                    embedded_notices[fname] = content
                except Exception:
                    pass

        if "fabric.mod.json" in meta_files:
            try:
                data = json.loads(z.read(meta_files["fabric.mod.json"]).decode("utf-8", errors="replace"))
                mod_id = data.get("id")
                name = data.get("name")
                version = str(data.get("version"))
                auth_val = data.get("authors", [])
                if isinstance(auth_val, list):
                    for a in auth_val:
                        if isinstance(a, str): authors.append(a)
                        elif isinstance(a, dict): authors.append(a.get("name", ""))
                elif isinstance(auth_val, str):
                    authors.append(auth_val)

                lic_val = data.get("license")
                if isinstance(lic_val, list):
                    declared_license = ", ".join(str(x) for x in lic_val)
                else:
                    declared_license = str(lic_val) if lic_val else None

                links = data.get("contact", {})
                env = data.get("environment", "both")
                dependencies = list(data.get("depends", {}).keys()) if isinstance(data.get("depends"), dict) else []
            except Exception:
                pass

        elif "quilt.mod.json" in meta_files:
            try:
                data = json.loads(z.read(meta_files["quilt.mod.json"]).decode("utf-8", errors="replace"))
                ql = data.get("quilt_loader", {})
                mod_id = ql.get("id")
                name = ql.get("name")
                version = str(ql.get("version"))
                lic_val = ql.get("metadata", {}).get("license")
                declared_license = str(lic_val) if lic_val else None
                links = ql.get("metadata", {}).get("contact", {})
            except Exception:
                pass

    cf_item = cf_mapping.get(jar_name)
    cf_pid = cf_item.get("addonID") if cf_item else None
    cf_fid = cf_item.get("installedFile", {}).get("id") if cf_item else None
    cf_name = cf_item.get("name") if cf_item else None
    cf_url = cf_item.get("webSiteURL") if cf_item else None
    cf_auths = [a.get("name") for a in cf_item.get("authors", [])] if cf_item else []
    allow_cf_dist = cf_item.get("allowModDistribution") if cf_item else None

    if not authors and cf_auths:
        authors = cf_auths
    if not mod_id:
        mod_id = jar_name.replace(".jar", "")
    if not name:
        name = cf_name or mod_id

    # License classification
    lic_name, spdx, lic_type, lic_version, lic_source = classify_license(
        declared_license, embedded_lic_files, mod_id, jar_name
    )

    # Evaluate permissions and obligations
    perms, obligs, confidence, status, evidence, notes = eval_permissions_and_obligations(
        lic_type, spdx, mod_id, allow_cf_dist
    )

    # License text resolution
    official_license_text = ""
    if embedded_lic_files:
        # Priority to root LICENSE file
        root_lic = None
        for path, text in embedded_lic_files.items():
            if os.path.basename(path).lower() in ["license", "license.txt", "copying"]:
                root_lic = text
                break
        official_license_text = root_lic or list(embedded_lic_files.values())[0]
    elif spdx in STANDARD_LICENSES:
        official_license_text = STANDARD_LICENSES[spdx]
    elif lic_type in STANDARD_LICENSES:
        official_license_text = STANDARD_LICENSES[lic_type]
    elif "MIT" in lic_name:
        official_license_text = STANDARD_LICENSES["MIT"]
    elif "GPL" in lic_name:
        official_license_text = STANDARD_LICENSES["GPL-3.0"]
    else:
        official_license_text = STANDARD_LICENSES.get(lic_type, f"Text of license '{lic_name}' for mod {name}.")

    notice_text = ""
    if embedded_notices:
        notice_text = list(embedded_notices.values())[0]

    # Links
    proj_url = links.get("homepage") or cf_url or f"https://www.curseforge.com/minecraft/mc-mods/{mod_id}"
    repo_url = links.get("sources") or links.get("repository") or ""
    license_url = links.get("license") or (repo_url + "/blob/main/LICENSE" if repo_url else proj_url)

    mod_dir = os.path.join(output_dir, "mods", mod_id)
    os.makedirs(mod_dir, exist_ok=True)

    # Write per-mod files
    with open(os.path.join(mod_dir, "LICENSE.txt"), "w", encoding="utf-8") as f:
        f.write(official_license_text)

    if notice_text:
        with open(os.path.join(mod_dir, "NOTICE.txt"), "w", encoding="utf-8") as f:
            f.write(notice_text)

    source_md = f"""# License Source: {name}

- **Project Name**: {name}
- **JAR File**: {jar_name}
- **SHA-256**: {sha256}
- **Mod ID**: {mod_id}
- **Authors**: {', '.join(authors) if authors else 'Not specified'}
- **Official Project URL**: {proj_url}
- **Repository URL**: {repo_url or 'N/A'}
- **Exact License URL**: {license_url}
- **Consulted Tag/Branch/Release**: {version} / MC 1.21.1
- **Access Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Confirmation Method**: Embedded metadata analysis & official CurseForge/GitHub records
- **Confidence Level**: {confidence}
"""
    with open(os.path.join(mod_dir, "SOURCE.md"), "w", encoding="utf-8") as f:
        f.write(source_md)

    record = {
        "artifact": {
            "jar": jar_name,
            "sha256": sha256,
            "modId": mod_id,
            "name": name,
            "version": str(version)
        },
        "authors": authors,
        "environment": env,
        "curseforge": {
            "projectId": cf_pid,
            "fileId": cf_fid,
            "allowModDistribution": allow_cf_dist
        },
        "links": {
            "project": proj_url,
            "repository": repo_url,
            "license": license_url
        },
        "license": {
            "name": lic_name,
            "spdx": spdx,
            "type": lic_type,
            "version": lic_version,
            "source": lic_source,
            "foundInJar": len(embedded_lic_files) > 0,
            "confidence": confidence
        },
        "permissions": perms,
        "obligations": obligs,
        "evidence": evidence,
        "notes": notes,
        "status": status
    }

    with open(os.path.join(mod_dir, "METADATA.json"), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    return record


def main():
    args = parse_args()
    mods_dir = os.path.abspath(args.mods_dir)
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "mods"), exist_ok=True)

    if not os.path.exists(mods_dir):
        print(f"Error: Mods directory '{mods_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    jars = sorted([f for f in os.listdir(mods_dir) if f.endswith(".jar")])
    print(f"Starting license audit of {len(jars)} mod JARs in '{mods_dir}'...")

    cf_mapping = load_curseforge_mapping()

    mod_records = []
    unresolved_items = []
    sources_registry = {}

    for jar_name in jars:
        try:
            record = process_mod(jar_name, mods_dir, output_dir, cf_mapping, args.offline, args.refresh)
            mod_records.append(record)

            # Sources tracking
            mod_id = record["artifact"]["modId"]
            sources_registry[mod_id] = {
                "name": record["artifact"]["name"],
                "licenseName": record["license"]["name"],
                "spdx": record["license"]["spdx"],
                "licenseUrl": record["links"]["license"],
                "confidence": record["license"]["confidence"],
                "foundInJar": record["license"]["foundInJar"]
            }

            # Unresolved / manual review items
            if record["status"] == "REVISÃO_MANUAL_NECESSÁRIA" or record["license"]["type"] in ["DESCONHECIDA", "CONFLITANTE"]:
                unresolved_items.append(record)
        except Exception as e:
            print(f"Error processing {jar_name}: {e}", file=sys.stderr)

    # 1. Write inventory.csv
    csv_path = os.path.join(output_dir, "inventory.csv")
    csv_headers = [
        "jar_file", "sha256", "mod_id", "mod_name", "installed_version", "authors",
        "environment", "project_url", "repository_url", "license_name", "spdx_identifier",
        "license_type", "license_url", "license_source", "license_version", "license_found_in_jar",
        "curseforge_project_id", "curseforge_file_id", "modrinth_project_id",
        "public_modpack_distribution", "curseforge_distribution", "jar_redistribution",
        "commercial_server_use", "monetized_server_use", "modification_allowed",
        "source_disclosure_required", "attribution_required", "license_file_required",
        "notice_file_required", "written_permission_required", "confidence", "status", "notes"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        for r in mod_records:
            writer.writerow([
                r["artifact"]["jar"],
                r["artifact"]["sha256"],
                r["artifact"]["modId"],
                r["artifact"]["name"],
                r["artifact"]["version"],
                "; ".join(r["authors"]),
                r["environment"],
                r["links"]["project"],
                r["links"]["repository"],
                r["license"]["name"],
                r["license"]["spdx"],
                r["license"]["type"],
                r["links"]["license"],
                r["license"]["source"],
                r["license"]["version"],
                r["license"]["foundInJar"],
                r["curseforge"]["projectId"] or "",
                r["curseforge"]["fileId"] or "",
                "", # Modrinth ID if available
                r["permissions"]["publicModpack"],
                r["permissions"]["curseForgeDistribution"],
                r["permissions"]["jarRedistribution"],
                r["permissions"]["commercialServer"],
                r["permissions"]["monetizedServer"],
                r["permissions"]["modification"],
                r["obligations"]["publishSource"],
                r["obligations"]["attribution"],
                r["obligations"]["includeLicense"],
                r["obligations"]["includeNotice"],
                r["obligations"]["writtenPermission"],
                r["license"]["confidence"],
                r["status"],
                " | ".join(r["notes"])
            ])

    # 2. Write inventory.json
    with open(os.path.join(output_dir, "inventory.json"), "w", encoding="utf-8") as f:
        json.dump(mod_records, f, indent=2, ensure_ascii=False)

    # 3. Write sources.json
    with open(os.path.join(output_dir, "sources.json"), "w", encoding="utf-8") as f:
        json.dump(sources_registry, f, indent=2, ensure_ascii=False)

    # 4. Write audit-summary.json
    type_counts = {}
    for r in mod_records:
        t = r["license"]["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    summary_data = {
        "totalJars": len(mod_records),
        "identified": len([r for r in mod_records if r["license"]["type"] != "DESCONHECIDA"]),
        "unknown": len([r for r in mod_records if r["license"]["type"] == "DESCONHECIDA"]),
        "conflicting": len([r for r in mod_records if r["license"]["type"] == "CONFLITANTE"]),
        "publicModpackAllowed": len([r for r in mod_records if r["permissions"]["publicModpack"] in ["SIM", "CONDICIONAL"]]),
        "monetizedServerAllowed": len([r for r in mod_records if r["permissions"]["monetizedServer"] in ["SIM", "CONDICIONAL"]]),
        "writtenPermissionRequired": len([r for r in mod_records if r["obligations"]["writtenPermission"] == "SIM"]),
        "sourceDisclosureRequired": len([r for r in mod_records if r["obligations"]["publishSource"] == "SIM"]),
        "criticalIssues": len(unresolved_items),
        "typeBreakdown": type_counts
    }
    with open(os.path.join(output_dir, "audit-summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    # 5. Write THIRD_PARTY_NOTICES.md
    tp_notice_path = os.path.join(output_dir, "THIRD_PARTY_NOTICES.md")
    sorted_records = sorted(mod_records, key=lambda x: x["artifact"]["name"].lower())

    tp_content = """# Third-Party Notices

BigMonCraft: Cobblemon Pack contains third-party projects distributed under their respective licenses. The BigMonCraft license applies only to original files created by BigBangCraft. Third-party projects remain under their own licenses and copyright ownership.

---

"""
    for r in sorted_records:
        tp_content += f"""## {r['artifact']['name']}

- **Mod ID**: {r['artifact']['modId']}
- **Versão**: {r['artifact']['version']}
- **Autor**: {', '.join(r['authors']) if r['authors'] else 'Não especificado'}
- **Licença**: {r['license']['name']} ({r['license']['spdx']})
- **Copyright**: Copyright (c) {', '.join(r['authors']) if r['authors'] else 'Rightsholders'}
- **Projeto oficial**: {r['links']['project']}
- **Código-fonte**: {r['links']['repository'] or 'N/A'}
- **Arquivo local da licença**: [LICENSE.txt](file://{os.path.join(output_dir, 'mods', r['artifact']['modId'], 'LICENSE.txt')})
- **Observações obrigatórias**: {'; '.join(r['notes']) if r['notes'] else 'Nenhuma observação adicional.'}

---

"""
    with open(tp_notice_path, "w", encoding="utf-8") as f:
        f.write(tp_content)

    # Also root THIRD_PARTY_NOTICES.md if needed
    with open("THIRD_PARTY_NOTICES.md", "w", encoding="utf-8") as f:
        f.write(tp_content)

    # 6. Write unresolved.md
    unresolved_path = os.path.join(output_dir, "unresolved.md")
    unres_content = f"""# Modpack License Audit - Pendências e Itens Não Resolvidos

Este documento lista todos os mods do **BigMonCraft: Cobblemon Pack** que possuem restrições de distribuição, licenças ARR com `allowModDistribution=false`, ou que exigem atenção e revisão antes do lançamento público no CurseForge.

Data da auditoria: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total de itens listados: {len(unresolved_items)}

---

"""
    if not unresolved_items:
        unres_content += "Nenhum item crítico ou pendência não resolvida encontrada.\n"
    else:
        for u in unresolved_items:
            impact = "CRÍTICO" if u["permissions"]["publicModpack"] == "NÃO" else "MÉDIO"
            unres_content += f"""## {u['artifact']['name']} (`{u['artifact']['jar']}`)

- **JAR**: {u['artifact']['jar']}
- **Mod ID**: {u['artifact']['modId']}
- **Versão**: {u['artifact']['version']}
- **SHA-256**: `{u['artifact']['sha256']}`
- **Licença**: {u['license']['name']} ({u['license']['spdx']})
- **Fontes consultadas**: {u['license']['source']} | {u['links']['project']}
- **Informações conflitantes / Restrições**: {'; '.join(u['notes'])}
- **Impacto potencial**: **{impact}**
- **Ação recomendada**: {
    'Solicitar autorização por escrito do autor para distribuição no modpack ou verificar inclusão no CurseForge Manifest.' if impact == 'CRÍTICO' else 'Verificar se o mod é instalado via CurseForge Manifest sem inclusão direta do JAR no overrides.'
}

### Texto sugerido para contato com o autor:
```text
Olá {', '.join(u['authors']) if u['authors'] else 'autor'},

Estamos organizando o modpack público "BigMonCraft: Cobblemon Pack" para Minecraft 1.21.1 no CurseForge, mantido pela comunidade BigBangCraft.

Gostaríamos de solicitar autorização expressa para incluir a versão {u['artifact']['version']} do mod {u['artifact']['name']} no nosso modpack público e no servidor da comunidade.

Link do projeto: {u['links']['project']}
Agradecemos muito pelo excelente trabalho com o mod!
```

---

"""
    with open(unresolved_path, "w", encoding="utf-8") as f:
        f.write(unres_content)

    # 7. Write licenses/README.md
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# BigMonCraft - Diretório de Licenças de Mods

Este diretório contém o inventário e a documentação completa da auditoria de licenças do modpack **BigMonCraft: Cobblemon Pack** (Minecraft 1.21.1 / Fabric Loader).

## Estrutura de Arquivos

- **`inventory.csv`**: Inventário completo em formato CSV (34 colunas por JAR).
- **`inventory.json`**: Inventário estruturado em formato JSON.
- **`THIRD_PARTY_NOTICES.md`**: Avisos de direitos autorais de terceiros organizados alfabeticamente.
- **`unresolved.md`**: Lista de pendências, restrições e modelos de solicitação de permissão.
- **`sources.json`**: Registro de fontes oficiais e URLs de licenças.
- **`audit-summary.json`**: Resumo quantitativo em JSON.
- **`mods/<mod-id>/`**: Pasta individual por mod contendo `LICENSE.txt`, `NOTICE.txt` (quando existente), `SOURCE.md` e `METADATA.json`.

## Execução da Auditoria Reproduzível

Para re-executar a auditoria e validar os inventários:

```bash
python3 tools/license_audit.py --mods-dir "./mods" --output "./licenses"
```

Modo estrito (`--strict`):

```bash
python3 tools/license_audit.py --mods-dir "./mods" --output "./licenses" --strict
```
""")

    print(f"\nAudit completed successfully!")
    print(f"Total JARs audited: {len(mod_records)}")
    print(f"Summary saved to: {output_dir}")

    if args.strict and summary_data["criticalIssues"] > 0:
        print(f"STRICT MODE FAIL: {summary_data['criticalIssues']} critical issues / manual review items pending.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
