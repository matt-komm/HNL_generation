BASEPATH=`pwd`

function run_steps()
{
    cmsRun -j FrameworkJobReport.xml -p PSet.py || return 1 
    mv $BASEPATH/HNL2018.root $BASEPATH/HNL_pu2018.root || return 1
    
    #PU -> AOD
    echo "============== PU -> AOD ===================="
    cmsDriver.py step2 \
       --filein file:$BASEPATH/HNL_pu2018.root \
       --fileout file:$BASEPATH/HNL_aod2018.root \
       --mc \
       --eventcontent AODSIM \
       --datatier AODSIM \
       --conditions 102X_upgrade2018_realistic_v15 \
       --step RAW2DIGI,L1Reco,RECO,RECOSIM,EI \
       --procModifiers premix_stage2 \
       --era Run2_2018 \
       --runUnscheduled \
       --python_filename pu2aod.py --no_exec \
       -n -1 || return 1
    cmsRun -p pu2aod.py || return 1
    
    #AOD -> MINIAOD
    echo "============== AOD -> MINIAOD ===================="
    cmsDriver.py step3 \
       --filein file:$BASEPATH/HNL_aod2018.root \
       --fileout file:$BASEPATH/HNL_miniaod2018.root \
       --mc \
       --eventcontent MINIAODSIM \
       --runUnscheduled \
       --datatier MINIAODSIM \
       --conditions 102X_upgrade2018_realistic_v15 \
       --step PAT \
       --geometry DB:Extended \
       --era Run2_2018 \
       --python_filename aod2miniaod.py --no_exec \
       -n -1 || return 1
    cmsRun -p aod2miniaod.py || return 1
    cd $BASEPATH
    
    mv $BASEPATH/HNL_miniaod2018.root $BASEPATH/HNL2018.root
}

run_steps

