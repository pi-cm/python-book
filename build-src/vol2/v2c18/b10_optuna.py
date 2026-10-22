import optuna
import torch

from 실험도구 import 로더_만들기, 모델_만들기, 씨앗_고정, 옷_데이터, 평가, 학습설정, 한_에폭_학습

optuna.logging.set_verbosity(optuna.logging.WARNING)     # 시도마다 찍는 안내 끄기
(X_학습, y_학습), (X_검증, y_검증), _ = 옷_데이터(학습_개수=20_000)


def 목적함수(시도: optuna.Trial) -> float:
    """Optuna가 고른 값으로 학습하고 검증 정확도를 돌려준다. 이 값을 키우는 것이 목표."""
    설정 = 학습설정(
        학습률=시도.suggest_float("학습률", 1e-4, 1e-1, log=True),     # 0.0001~0.1, 로그 눈금
        드롭아웃=시도.suggest_float("드롭아웃", 0.0, 0.5),
        가중치_감쇠=시도.suggest_float("가중치_감쇠", 1e-6, 1e-1, log=True),
        배치_크기=시도.suggest_categorical("배치_크기", [32, 64, 128, 256]),
        에폭=3, 학습_개수=20_000,
    )
    씨앗_고정(설정.씨앗)
    모델 = 모델_만들기(설정)
    옵티마이저 = torch.optim.AdamW(모델.parameters(), lr=설정.학습률, weight_decay=설정.가중치_감쇠)
    로더 = 로더_만들기(X_학습, y_학습, 설정.배치_크기, 설정.씨앗)
    for _ in range(설정.에폭):
        한_에폭_학습(모델, 로더, 옵티마이저)
    return 평가(모델, X_검증, y_검증)[1]


for 이름, 고르개 in [("무작위", optuna.samplers.RandomSampler(seed=0)),
                    ("TPE", optuna.samplers.TPESampler(seed=0))]:
    연구 = optuna.create_study(direction="maximize", sampler=고르개)
    연구.optimize(목적함수, n_trials=30)
    값들 = [t.value for t in 연구.trials]
    print(f"[{이름}] 최고 {연구.best_value:.2%} ({연구.best_trial.number + 1}번째 시도)")
    print("  최고 설정:", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in 연구.best_params.items()})
    print("  처음 10번:", " ".join(f"{v:.3f}" for v in 값들[:10]))
    print("  나중 20번:", " ".join(f"{v:.3f}" for v in 값들[10:]))
    print(f"  나중 20번 평균 {sum(값들[10:]) / 20:.2%}, 80% 미만 {sum(v < 0.8 for v in 값들)}번")
