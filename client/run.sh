# SUPPORT_MODEL_REF = [
#     "gpt-4o-mini-0718", "gpt-4o-0806", "gpt-4-0409",
#     "gemini-1.5-pro", "gemini-1.5-pro-flash",
#     "qwen_max", "qwen2.5-72b-instruct", "qwen2.5-7b-instruct",
#     "claude35_sonnet", 

#     "o1-preview-0912", "o1-mini-0912",
#     "qwq-32b", "qwen_max", "claude37_sonnet"
# ]
python client/powerInstruct.py \
    --max_iterations 10 \
    --min_accuacy 0.98 \
    --delta_accuracy 0.005 \
    --test_sample_ratio 0.3 \
    --model_codegen "claude37_sonnet" \
    --model_datagen "o1-mini-0912" \
    --api_url "http://localhost:5000/analyze" \
    --clean_url "http://localhost:5000/clean"
