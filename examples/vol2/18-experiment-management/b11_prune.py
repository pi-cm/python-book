# [2권 Chapter 18. 실험 관리와 재현성 · 18.5 하이퍼파라미터 탐색 자동화 · manuscript-vol2/chapters/18-experiment-management.md:894]
import optuna
import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

optuna.logging.set_verbosity(optuna.logging.WARNING)
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(학습_개수=20_000)
최대_에폭 = 5


def 목적함수(시도: optuna.Trial) -> float:
    설정 = 학습설정(
        학습률=시도.suggest_float("학습률", 1e-4, 1e-1, log=True),
        드롭아웃=시도.suggest_float("드롭아웃", 0.0, 0.5),
        가중치_감쇠=시도.suggest_float("가중치_감쇠", 1e-6, 1e-1, log=True),
        배치_크기=시도.suggest_categorical("배치_크기", [32, 64, 128, 256]),
        에폭=최대_에폭, 학습_개수=20_000,
    )
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=설정.학습률, weight_decay=설정.가중치_감쇠)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    for 에폭 in range(1, 설정.에폭 + 1):
        한_에폭_학습(모델, 로더, 옵티마이저)
        정확도 = 평가(모델, X_검증, y_검증)[1]
        시도.report(정확도, 에폭)             # 중간 성적 알리기
        시도.set_user_attr("에폭", 에폭)
        if 시도.should_prune():               # 지금까지의 시도들 중간값보다 못하면
            raise optuna.TrialPruned()        # 여기서 그만
    return 정확도


연구 = optuna.create_study(
    study_name="옷-가지치기", storage="sqlite:///탐색.db",       # 기록을 파일에 남긴다
    direction="maximize", sampler=optuna.samplers.TPESampler(seed=0),
    pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=2),
)
연구.optimize(목적함수, n_trials=40)

끝까지 = [t for t in 연구.trials if t.state == optuna.trial.TrialState.COMPLETE]
잘림 = [t for t in 연구.trials if t.state == optuna.trial.TrialState.PRUNED]
쓴_에폭 = sum(t.user_attrs["에폭"] for t in 연구.trials)
print(f"끝까지 학습 {len(끝까지)}번, 중간에 멈춤 {len(잘림)}번")
print(f"학습한 에폭 {쓴_에폭} / 가지치기가 없었다면 {len(연구.trials) * 최대_에폭}")
print(f"최고 검증 정확도 {연구.best_value:.2%} ({연구.best_trial.number + 1}번째 시도)")
print("멈춘 에폭별 개수:", {e: sum(t.user_attrs['에폭'] == e for t in 잘림) for e in range(1, 최대_에폭 + 1)})
