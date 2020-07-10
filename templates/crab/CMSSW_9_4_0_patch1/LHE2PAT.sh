BASEPATH=`pwd`

function run_steps()
{
    cmsRun -j FrameworkJobReport.xml -p PSet.py || return 1 
    mv $BASEPATH/HNL2017.root $BASEPATH/HNL_pu2017.root || return 1
    
    mkdir $BASEPATH/.temp || return 1
    cd $BASEPATH/.temp || return 1
    
    scramv1 project CMSSW CMSSW_9_4_7 || return 1
    cd $BASEPATH/.temp/CMSSW_9_4_7/src || return 1
    eval `scram runtime -sh` || return 1
    
    #PU -> AOD
    echo "============== PU -> AOD ===================="
    cmsDriver.py step2 \
       --filein file:$BASEPATH/HNL_pu2017.root \
       --fileout file:$BASEPATH/HNL_aod2017.root \
       --mc \
       --eventcontent AODSIM \
       --datatier AODSIM \
       --conditions 94X_mc2017_realistic_v11 \
       --step RAW2DIGI,RECO,RECOSIM,EI \
       --era Run2_2017 \
       --runUnscheduled \
       --python_filename pu2aod.py --no_exec \
       -n -1 || return 1
    cmsRun -p pu2aod.py || return 1
    
    #AOD -> MINIAOD
    echo "============== AOD -> MINIAOD ===================="
    cd $BASEPATH/.temp/CMSSW_9_4_7/src || return 1
    cmsDriver.py step3 \
       --filein file:$BASEPATH/HNL_aod2017.root \
       --fileout file:$BASEPATH/HNL_miniaod2017.root \
       --mc \
       --eventcontent MINIAODSIM \
       --runUnscheduled \
       --datatier MINIAODSIM \
       --conditions 94X_mc2017_realistic_v14 \
       --step PAT \
       --scenario pp \
       --era Run2_2017,run2_miniAOD_94XFall17 \
       --python_filename aod2miniaod.py --no_exec \
       -n -1 || return 1
    cmsRun -p aod2miniaod.py || return 1
    cd $BASEPATH
    
    mv $BASEPATH/HNL_miniaod2017.root $BASEPATH/HNL2017.root
}

run_steps

