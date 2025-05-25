set -ex

export CUDA_VISIBLE_DEVICES=1

declare -A TASK_DATA

TASK_DATA[eae]='ere_en_030' 
DATA_RATIOS="0.3"

SEEDS="2024 20011010 42 3407"

echo $SEEDS

LEARNING_RATE="1e-4 9e-5"

BATCHS="16 8"
BATCHS="16"

EPOCHS="40 60"


RESULT_CSV_COLLECT_FILE="../2-20241201-results-t5_large-030.csv"

cd src

# check whether exists the file 'result.csv'
if [ ! -f "$RESULT_CSV_COLLECT_FILE" ]; then
    # mkdir -p $RESULT_CSV_COLLECT_FILE
    echo "DATA,EPOCH,BATCH,LEARNING,8,SEED,OUT_DIR,current_time,arg_p,arg_r,arg_f,p,r,f" > "$RESULT_CSV_COLLECT_FILE"
    echo "TASK_DATA,EPOCH,train_batch_size,learning_rate,eval_batch_size,seed,(OUT_DIR),Current_time,arg_I_prec,arg_I_rec,arg_I_f1,precision,recall,F1" >> "$RESULT_CSV_COLLECT_FILE"
fi



for TASK in eae
do
for DATA in ${TASK_DATA[${TASK}]}
do
for DATA_RATIO in ${DATA_RATIOS}
do
for BATCH in ${BATCHS}
do
for K in 4 # for K in 3 7 15
do
for SEED in ${SEEDS}
do
for EPOCH in ${EPOCHS}
do
for LEARNING in ${LEARNING_RATE}
do
INFER_PATH=$K
CTRL_TOKEN=post
OUT_DIR="../outputs/$TASK/${DATA}/20241201_top${K}_${CTRL_TOKEN}_data${DATA_RATIO}_seed${SEED}_epoch${EPOCH}_batch${BATCH}_lr${LEARNING}_t5_large-030"
# OUT_DIR="../outputs/$TASK/${DATA}/top${K}_${CTRL_TOKEN}_data${DATA_RATIO}"

mkdir -p $OUT_DIR

echo "=========================================="
echo "${OUT_DIR}"
echo "=========================================="

python main.py \
    --data_path "../data" \
    --dataset $DATA \
    --model_name_or_path "../model/t5-large" \
    --output_dir $OUT_DIR \
    --num_train_epochs $EPOCH \
    --save_top_k 0 \
    --task $TASK \
    --top_k $K \
    --ctrl_token $CTRL_TOKEN \
    --multi_path \
    --num_path $INFER_PATH \
    --seed $SEED \
    --train_batch_size $BATCH \
    --gradient_accumulation_steps 1 \
    --learning_rate $LEARNING \
    --lowercase \
    --sort_label \
    --data_ratio $DATA_RATIO \
    --check_val_every_n_epoch 10  \
    --agg_strategy vote \
    --eval_batch_size 8 \
    --constrained_decode True \
    --do_train \
    | tee ${OUT_DIR}/train.log \
    2> ${OUT_DIR}/train.err
    # --model_name_or_path "PATH TO THE CHECKPOINT" \ # configure the checkpoint path to eval

    # --load_path_cache \
    # --single_view_type $SVP_TYPE \
    # --load_ckpt_name "ckpt path" \
    # > $OUT_DIR/train.log 2>&1&



FILE_PATH="$OUT_DIR/result.txt"
# arg-I
arg_p=0
arg_r=0
arg_f=0
# arg-C
p=0
r=0
f=0


if [ -f "$FILE_PATH" ]; then

    line=$(sed -n '2p' "$FILE_PATH")

    if [[ $line =~ arg_prec:\ ([0-9]+\.[0-9]+)\ arg_rec:\ ([0-9]+\.[0-9]+)\ arg_f1:\ ([0-9]+\.[0-9]+)\ Arg_I:\ precision:\ ([0-9]+\.[0-9]+)\ recall:\ ([0-9]+\.[0-9]+)\ F1\ =\ ([0-9]+\.[0-9]+) ]]; then
        arg_p=${BASH_REMATCH[1]}
        arg_r=${BASH_REMATCH[2]}
        arg_f=${BASH_REMATCH[3]}
        p=${BASH_REMATCH[4]}
        r=${BASH_REMATCH[5]}
        f=${BASH_REMATCH[6]}
    fi
fi

# result output 
echo "arg-I"
echo "Precision: $arg_p"
echo "Recall: $arg_r"
echo "F1: $arg_f"
echo "arg-C"
echo "Precision: $p"
echo "Recall: $r"
echo "F1: $f"

current_time=$(date +"%Y-%m-%d_%H:%M:%S")
echo "Current time: $current_time"


# add result to 'result.csv'
# TASK_DATA	num_train_epochs	train_batch_size	learning_rate	eval_batch_size	seed	权重保存目录(OUT_DIR)   Current_time	precision	recall	F1
echo "$DATA,$EPOCH,$BATCH,$LEARNING,8,$SEED,$OUT_DIR,$current_time,$arg_p,$arg_r,$arg_f,$p,$r,$f" >> "$RESULT_CSV_COLLECT_FILE"



done
done
done
done
done
done
done
done
# done





            # "args" : [
            #     "--data_path", "./data/",
            #     "--dataset", "ACE05_EN_EAE",
            #     "--model_name_or_path", "./model/t5-base/",
            #     "--output_dir", "./outputs/eae/ACE05_EN_EAE/top5_post_data1.0_seed5",
            #     "--num_train_epochs", "2",
            #     "--task", "eae",
            #     "--top_k", "5",
            #     "--multi_path",
            #     "--num_path", "5",
            #     "--seed", "5",
            #     "--lowercase", "--sort_label", "--constrained_decode", "--do_train"
            # ]            