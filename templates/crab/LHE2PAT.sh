BASEPATH=`pwd`

function run_steps()
{
    cmsRun -j FrameworkJobReport.xml -p PSet.py || return 1 
    mv $BASEPATH/HNL2016.root $BASEPATH/HNL_pu2016.root || return 1
    
    mkdir $BASEPATH/.temp || return 1
    
    #PU -> AOD
    echo "============== PU -> AOD ===================="
    cmsDriver.py step2 \
       --filein file:$BASEPATH/HNL_pu2016.root \
       --fileout file:$BASEPATH/HNL_aod2016.root \
       --mc \
       --eventcontent AODSIM \
       --datatier AODSIM \
       --conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6 \
       --step RAW2DIGI,RECO,EI \
       --era Run2_2016 \
       --python_filename pu2aod.py --no_exec \
       -n -1 || return 1
    cmsRun -p pu2aod.py || return 1
    cd $BASEPATH
    
    #AOD -> MINIAOD
    echo "============== AOD -> MINIAOD ===================="
    cd $BASEPATH/.temp || return 1
    scramv1 project CMSSW CMSSW_9_4_9 || return 1
    cd $BASEPATH/.temp/CMSSW_9_4_9/src || return 1
    eval `scram runtime -sh` || return 1
    cmsDriver.py step3 \
       --filein file:$BASEPATH/HNL_aod2016.root \
       --fileout file:$BASEPATH/HNL_miniaod2016.root \
       --mc \
       --eventcontent MINIAODSIM \
       --datatier MINIAODSIM \
       --conditions 94X_mcRun2_asymptotic_v3 \
       --step PAT \
       --runUnscheduled \
       --era Run2_2016,run2_miniAOD_80XLegacy \
       --python_filename aod2miniaod.py --no_exec \
       -n -1 || return 1
    cmsRun -p aod2miniaod.py || return 1
    cd $BASEPATH
    
    mv $BASEPATH/HNL_miniaod2016.root $BASEPATH/HNL2016.root
}

run_steps

