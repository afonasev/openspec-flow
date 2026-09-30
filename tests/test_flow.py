import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'template/tools/flow.py'
spec=importlib.util.spec_from_file_location('flow',SCRIPT); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        (self.root/'openspec/changes').mkdir(parents=True); self.f=m.Flow(self.root)
    def tearDown(self):self.tmp.cleanup()
    def new(self,cid='example',kind='report',route='quick',parent=None):
        p=self.root/'openspec/changes'/cid;p.mkdir();(p/'.openspec.yaml').write_text('schema: flow-quick\n')
        return self.f.init(cid,route,kind,parent)
    def ready(self,cid='example'):
        self.f.evidence(cid,'scope',{'approved':True});self.f.transition(cid,'ready')
    def report_delivered(self,cid='example'):
        self.ready(cid);self.f.claim(cid,'worker');self.f.transition(cid,'implementing','worker')
        self.f.evidence(cid,'verification',{'result':'pass'});self.f.transition(cid,'verified','worker')
        self.f.evidence(cid,'publication',{'path':'durable/report.md'});self.f.transition(cid,'published','worker')
        self.f.transition(cid,'finalizing','worker')
    def finalize(self,cid='example'):
        for k in ['spec_sync','cleanup']:self.f.evidence(cid,k,{'result':'verified'})
        (self.f.get(cid)[0].parent/'acceptance.md').write_text('Review the published report.')
        self.f.evidence(cid,'acceptance_guide','acceptance.md');self.f.transition(cid,'awaiting-acceptance','worker')
    def test_report_acceptance_and_archive(self):
        self.new();self.report_delivered();self.finalize()
        with self.assertRaises(ValueError):self.f.transition('example','accepted')
        self.f.transition('example','accepted',decision='Все устраивает',source='user message 42')
        self.f.evidence('example','archive',{'commit':'recorded'})
        with self.assertRaises(ValueError):self.f.transition('example','archived')
        dest=self.root/'openspec/changes/archive/2026-09-20-example';dest.parent.mkdir();self.f.get('example')[0].parent.rename(dest)
        self.f.transition('example','archived')
    def test_unresolved_question_and_inline_answer(self):
        self.new();self.f.question('example','What behavior?',['ready']);self.f.evidence('example','scope','agreed')
        with self.assertRaises(ValueError):self.f.transition('example','ready')
        self.f.answer('example','Q1','A','user message')
        with self.assertRaises(ValueError):self.f.transition('example','ready')
        self.f.answer('example','Q1','A','user message','Spec updated');self.f.transition('example','ready')
        self.assertFalse(self.f.inbox()[0]['questions'])
    def test_no_double_claim_concurrent_processes(self):
        self.new();self.ready()
        cmds=[[ 'python3',str(SCRIPT),'--root',str(self.root),'claim','example','--owner',o] for o in ['one','two']]
        ps=[subprocess.Popen(c,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for c in cmds]
        results=[(p.communicate(),p.returncode)[1] for p in ps]
        self.assertEqual(sorted(results),[0,2])

    def test_delivery_debt_and_rework_reset(self):
        self.new();self.report_delivered()
        self.assertTrue(self.f.inbox()[0]['finalization_debt'])
        with self.assertRaises(ValueError):self.f.transition('example','awaiting-acceptance','worker')
        self.finalize();self.f.transition('example','rework-required',decision='Fix totals',source='inline feedback')
        self.assertEqual(set(self.f.get('example')[1]['evidence']),{'scope'})
        self.f.claim('example','new-worker');self.f.transition('example','implementing','new-worker')
        with self.assertRaises(ValueError):self.f.transition('example','verified','new-worker')
    def test_dependencies_and_cycles(self):
        self.new('first');self.new('second');self.f.dependency('second','first','delivered')
        self.f.evidence('second','scope','agreed')
        with self.assertRaises(ValueError):self.f.transition('second','ready')
        with self.assertRaises(ValueError):self.f.dependency('first','second','accepted')
        self.report_delivered('first');self.f.transition('second','ready')
    def test_initiative_child_gate(self):
        self.new('campaign','initiative','initiative');self.new('mission',parent='campaign')
        with self.assertRaises(ValueError):self.f.dependency('mission','campaign','accepted')
        self.report_delivered('campaign')
        for k in ['spec_sync','cleanup']:self.f.evidence('campaign',k,'checked')
        (self.f.get('campaign')[0].parent/'acceptance.md').write_text('Whole campaign')
        self.f.evidence('campaign','acceptance_guide','acceptance.md')
        with self.assertRaises(ValueError):self.f.transition('campaign','awaiting-acceptance','worker')
    def test_merge_real_ancestry(self):
        repo=self.root/'code';repo.mkdir()
        def git(*args):return subprocess.check_output(['git','-C',str(repo),*args],stderr=subprocess.DEVNULL,text=True).strip()
        git('init','-b','main');git('config','user.email','test@example.invalid');git('config','user.name','Test')
        (repo/'a').write_text('a');git('add','.');git('commit','-m','base')
        git('checkout','-b','feature');(repo/'a').write_text('b');git('commit','-am','feature');sha=git('rev-parse','HEAD')
        self.new(kind='software');self.ready();self.f.claim('example','worker');self.f.transition('example','implementing','worker')
        self.f.evidence('example','verification','pass');self.f.evidence('example','commit',sha);self.f.transition('example','verified','worker')
        self.f.evidence('example','merge',{'repo':str(repo),'commit':sha,'main_ref':'main'})
        with self.assertRaises(subprocess.CalledProcessError):self.f.transition('example','merged','worker')
        git('checkout','main');git('merge','--ff-only','feature');self.f.transition('example','merged','worker')
    def test_lease_ownership(self):
        self.f.lease('acquire','integration','a')
        with self.assertRaises(ValueError):self.f.lease('acquire','integration','b')
        with self.assertRaises(ValueError):self.f.lease('release','integration','b')
        self.f.lease('release','integration','a');self.f.lease('acquire','integration','b')
    def test_explicit_standalone_profile_keeps_root_coordination(self):
        (self.root/'workflow').mkdir()
        (self.root/'workflow/project.json').write_text(json.dumps({'planning_layout':'standalone'}))
        f=m.Flow(self.root)
        self.assertEqual(f.coordination,self.root.resolve())
        f.lease('acquire','planning','owner')
        self.assertTrue((self.root/'.flow-leases.json').is_file())
    def test_pause_is_sticky(self):
        self.new();self.ready();p,d=self.f.get('example');d['paused']=True;self.f.save(p,d,'paused')
        self.assertFalse(self.f.inbox()[0]['ready'])
        with self.assertRaises(ValueError):self.f.claim('example','worker')


class LinkedWorktrees(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();base=Path(self.tmp.name)
        self.main=base/'project';self.one=base/'one';self.two=base/'two'
        self.main.mkdir()
        self.git(self.main,'init','-b','main')
        self.git(self.main,'config','user.email','flow@example.test')
        self.git(self.main,'config','user.name','Flow Test')
        (self.main/'openspec/changes/example').mkdir(parents=True)
        (self.main/'openspec/changes/example/.openspec.yaml').write_text('schema: flow-quick\n')
        (self.main/'workflow').mkdir()
        (self.main/'workflow/project.json').write_text(json.dumps({'planning_layout':'in-repo','main_branch':'main'}))
        self.git(self.main,'add','.')
        self.git(self.main,'commit','-m','Initial planning')
        self.git(self.main,'worktree','add','-b','one',str(self.one),'main')
        self.git(self.main,'worktree','add','-b','two',str(self.two),'main')
        self.f1=m.Flow(self.one);self.f2=m.Flow(self.two)
        self.f1.init('example',kind='report',route='quick')
        self.f1.evidence('example','scope',{'approved':True})
        self.f1.transition('example','ready')

    def tearDown(self):self.tmp.cleanup()

    def git(self,root,*args):
        return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True,text=True).stdout

    def test_shared_pointer_and_lease(self):
        self.assertEqual(self.f2.get('example')[1]['stage'],'ready')
        self.assertEqual(self.f1.coordination,self.f2.coordination)
        self.f1.lease('acquire','integration','one')
        with self.assertRaisesRegex(ValueError,'Lease held'):
            self.f2.lease('acquire','integration','two')
        self.f1.lease('release','integration','one')
        cmds=[['python3',str(SCRIPT),'--root',str(root),'claim','example','--owner',owner]
              for root,owner in [(self.one,'one'),(self.two,'two')]]
        ps=[subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for cmd in cmds]
        results=[]
        for p in ps:
            p.communicate();results.append(p.returncode)
        self.assertEqual(sorted(results),[0,2])

    def test_concurrent_claim_after_record_is_integrated(self):
        self.git(self.one,'add','openspec')
        self.git(self.one,'commit','-m','Prepare ready change')
        self.git(self.main,'merge','--ff-only','one')
        self.f1.unpin('example')
        self.git(self.two,'merge','main')
        cmds=[['python3',str(SCRIPT),'--root',str(root),'claim','example','--owner',owner]
              for root,owner in [(self.one,'one'),(self.two,'two')]]
        ps=[subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for cmd in cmds]
        results=[]
        for p in ps:
            p.communicate();results.append(p.returncode)
        self.assertEqual(sorted(results),[0,2])
        self.assertIn(self.f1.pins()['example']['owner'],{'one','two'})

    def test_stale_worktree_cannot_reclaim_completed_change(self):
        self.f1.claim('example','one')
        self.f1.transition('example','cancelled','one',decision='Cancelled',source='user')
        with self.assertRaisesRegex(ValueError,'integrate the exact delivery record'):
            self.f1.unpin('example')
        self.git(self.one,'add','openspec')
        self.git(self.one,'commit','-m','Record cancellation')
        self.git(self.main,'merge','--ff-only','one')
        self.f1.unpin('example')
        with self.assertRaisesRegex(ValueError,'behind main'):
            self.f2.claim('example','two')
        self.git(self.two,'merge','main')
        with self.assertRaisesRegex(ValueError,'Not claimable'):
            self.f2.claim('example','two')
        self.assertEqual(self.f2.inbox()[0]['stage'],'cancelled')

    def test_handoff_keeps_record_after_worker_worktree_removed(self):
        self.f1.claim('example','one')
        self.git(self.one,'add','openspec')
        self.git(self.one,'commit','-m','Record claim')
        self.git(self.main,'merge','--ff-only','one')
        stable=m.Flow(self.main)
        stable.handoff('example')
        with self.assertRaisesRegex(ValueError,'belongs to another worktree'):
            self.f1.evidence('example','verification',{'result':'pass'})
        self.git(self.main,'worktree','remove',str(self.one))
        self.assertEqual(stable.get('example')[1]['owner'],'one')
        stable.release('example','one')
        with self.assertRaisesRegex(ValueError,'integrate the exact delivery record'):
            stable.unpin('example')
        self.git(self.main,'add','openspec')
        self.git(self.main,'commit','-m','Release claim')
        stable.unpin('example')
        self.assertIsNone(stable.get('example')[1]['owner'])
if __name__=='__main__':unittest.main()
