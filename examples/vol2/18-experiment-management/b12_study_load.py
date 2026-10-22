# [2권 Chapter 18. 실험 관리와 재현성 · 18.5 하이퍼파라미터 탐색 자동화 · manuscript-vol2/chapters/18-experiment-management.md:958]
import optuna

optuna.logging.set_verbosity(optuna.logging.WARNING)

# 앞 절에서 탐색.db에 남긴 연구를 이름으로 다시 연다 (프로그램을 껐다 켜도 그대로)
연구 = optuna.load_study(study_name="옷-가지치기", storage="sqlite:///탐색.db")
print(f"불러온 시도 {len(연구.trials)}개, 최고 {연구.best_value:.2%}")

# 시도 기록을 pandas 표로: 끝까지 학습한 것 중 위에서 다섯
표 = 연구.trials_dataframe(attrs=("number", "value", "params", "state"))
표 = 표[표.state == "COMPLETE"].sort_values("value", ascending=False).head(5)
for _, 줄 in 표.iterrows():
    print(f"{줄.number + 1:2}번째 {줄.value:.2%}  학습률 {줄.params_학습률:.5f}  드롭아웃 {줄.params_드롭아웃:.2f}  "
          f"감쇠 {줄.params_가중치_감쇠:.1e}  배치 {줄.params_배치_크기}")

# 어떤 값이 결과를 가장 많이 흔들었나
중요도 = optuna.importance.get_param_importances(연구, evaluator=optuna.importance.FanovaImportanceEvaluator(seed=0))
for 이름, 값 in 중요도.items():
    print(f"중요도 {이름}: {값:.2f}")
