# [2권 Chapter 18. 실험 관리와 재현성 · 18.4 실험 기록 남기기 · manuscript-vol2/chapters/18-experiment-management.md:750]
from dataclasses import asdict, replace

import mlflow
import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

mlflow.set_tracking_uri("sqlite:///mlflow.db")        # 기록은 이 폴더의 SQLite 파일 하나에
mlflow.set_experiment("옷분류-학습률")
기준 = 학습설정(에폭=4, 학습_개수=10_000)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(기준.학습_개수)

for 학습률 in (3e-4, 1e-3, 3e-3, 1e-2):
    설정 = replace(기준, 학습률=학습률)
    with mlflow.start_run(run_name=f"mlp lr={학습률:g}"):
        mlflow.log_params(asdict(설정))                  # 설정 전부
        mlflow.set_tag("메모", "학습률만 바꿔 본 실험")
        씨앗_고정(설정.씨앗)
        모델 = 모델_만들기(설정)
        옵티마이저 = torch.optim.Adam(모델.parameters(), lr=설정.학습률)
        로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
        for 에폭 in range(1, 설정.에폭 + 1):
            학습_손실 = 한_에폭_학습(모델, 로더, 옵티마이저)
            검증_손실, 검증_정확도 = 평가(모델, X_검증, y_검증)
            mlflow.log_metrics({"학습_손실": 학습_손실, "검증_손실": 검증_손실,
                                "검증_정확도": 검증_정확도}, step=에폭)
        torch.save(모델.state_dict(), "모델.pt")
        mlflow.log_artifact("모델.pt")                   # 파일도 실험에 붙여 둔다

# 기록을 표로 꺼내 비교하기 (pandas DataFrame)
표 = mlflow.search_runs(experiment_names=["옷분류-학습률"], order_by=["metrics.검증_정확도 DESC"])
for _, 줄 in 표.iterrows():
    print(f"{줄['tags.mlflow.runName']:13} 학습률 {줄['params.학습률']:>6}  "
          f"검증 정확도 {줄['metrics.검증_정확도']:.2%}  검증 손실 {줄['metrics.검증_손실']:.4f}")

# 실험 하나의 에폭별 기록과 붙여 둔 파일
최고 = 표.iloc[0]
이력 = mlflow.MlflowClient().get_metric_history(최고.run_id, "검증_정확도")
print("에폭별 검증 정확도:", [(m.step, round(m.value, 4)) for m in 이력])
print("붙여 둔 파일:", [f.path for f in mlflow.MlflowClient().list_artifacts(최고.run_id)])
