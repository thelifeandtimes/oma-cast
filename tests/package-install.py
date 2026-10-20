#!/usr/bin/env python3
# Exercise the installed Omarchy CLI in a temporary home using local Git repos.
# Shell IPC is stubbed; no plugins are loaded into the desktop.
from pathlib import Path
import os, json, shutil, subprocess, tempfile
repo=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='oma-cast-native-install-') as tmp:
    stage=Path(tmp)
    source=stage/'source'; source.mkdir()
    shutil.copy2(repo/'manifest.json', source/'manifest.json')
    shutil.copytree(repo/'plugin', source/'plugin')
    shutil.copytree(repo/'bin', source/'bin')
    test_home=stage/'home'; test_home.mkdir()
    mockbin=stage/'bin'; mockbin.mkdir()
    omarchy=stage/'omarchy'; (omarchy/'shell/plugins').mkdir(parents=True)
    env=dict(os.environ, HOME=str(test_home), PATH=str(mockbin)+':'+os.environ['PATH'], OMARCHY_PATH=str(omarchy), GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null')
    (mockbin/'omarchy-shell').write_text('''#!/bin/bash
set -eu
case "$*" in
  'shell rescanPlugins') echo ok ;;
  'shell listPlugins')
    if [[ -f "$HOME/.config/omarchy/plugins/thelifeandtimes.oma-cast/manifest.json" ]]; then
      enabled=false; [[ ! -f "$HOME/enabled" ]] || enabled=true
      jq --argjson enabled "$enabled" '[. + {enabled: $enabled, firstParty: false}]' "$HOME/.config/omarchy/plugins/thelifeandtimes.oma-cast/manifest.json"
    else echo '[]'; fi ;;
  'shell enablePlugin thelifeandtimes.oma-cast {}') touch "$HOME/enabled"; echo ok ;;
  'shell setPluginEnabled thelifeandtimes.oma-cast false') rm "$HOME/enabled"; echo ok ;;
  'shell ping'|'oma-cast ping') echo ok ;;
  'oma-cast call system.healthPing {}') echo '{"ok":true,"data":null}' ;;
  *) echo "Unexpected shell call: $*" >&2; exit 1 ;;
esac
''')
    (mockbin/'omarchy-shell').chmod(0o755)
    (mockbin/'hyprctl').write_text('#!/bin/bash\n[[ $* == version ]]\n')
    (mockbin/'hyprctl').chmod(0o755)
    def run(*args, cwd=None):
        r=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True,timeout=20)
        if r.returncode: raise RuntimeError(str(args)+'\n'+r.stdout+r.stderr)
        return r.stdout.strip()
    def commit(message):
        run('git','add','.',cwd=source)
        run('git','-c','user.name=Packaging Test','-c','user.email=test@example.invalid','commit','-qm',message,cwd=source)
    run('git','init','-q','-b','main',str(source))
    commit('Initial fixture')
    print(run('omarchy','plugin','install',str(source),'--yes','--enable'))
    target=test_home/'.config/omarchy/plugins/thelifeandtimes.oma-cast'
    assert (target/'.git').is_dir() and not target.is_symlink()
    assert (test_home/'enabled').is_file()
    print(run(str(target/'bin/oma-cast'),'doctor'))
    for old in ('install','uninstall','reload','dev','setup'):
        p=subprocess.run([str(target/'bin/oma-cast'),old],env=env,capture_output=True,text=True,timeout=5)
        assert p.returncode != 0 and (target/'.git').is_dir(), old
    manifest=json.loads((source/'manifest.json').read_text())
    manifest['version']='0.0.3-test'
    (source/'manifest.json').write_text(json.dumps(manifest))
    commit('Update fixture')
    print(run('omarchy','plugin','update','thelifeandtimes.oma-cast','--yes'))
    assert json.loads((target/'manifest.json').read_text())['version']=='0.0.3-test'
    assert run('git','rev-parse','HEAD',cwd=target)==run('git','rev-parse','HEAD',cwd=source)
    print(run('omarchy','plugin','remove','thelifeandtimes.oma-cast','--yes'))
    assert not target.exists() and not (test_home/'enabled').exists()
    print('PASS: native Git install/enable, doctor, retired helper commands, fast-forward update, disable/remove; only shell IPC and hyprctl were stubbed.')
