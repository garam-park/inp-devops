# 기대 차이 — jeju-ai 프로토타입 ↔ 제품 저장소

`scripts/check-jeju-ai-parity.sh` 가 이 폴더를 기준선으로 삼는다.
여기 있는 `.diff` 는 **의도된 차이**다 — 경로·환경변수와 "이 저장소 전용" 부분뿐이다.

| 파일 | 남는 차이 |
| --- | --- |
| `gislib.py.diff` | 없음 — 두 저장소가 바이트 동일 |
| `build_data.py.diff` | 실행 안내 · 결과 폴더(`app/public/data` ↔ `DATA_DIR`) · 캐시 폴더 · 지수 실행기 안내 · `catalog.json` 직접 만들기 |
| `run_index.py.diff` | 실행 안내 · `DATA_DIR` 설명 · 자료 폴더 |
| `geocode_excavation.py.diff` | 실행 안내 · 브이월드 키(`VITE_VWORLD_KEY` ↔ `VWORLD_KEY`) · 캐시 폴더 |

## 언제 바뀌는가

원본(`jeju-ai-saas-be/pipeline`)이 바뀌면 여기의 기대도 바뀐다. 그때는 아래 순서로 한다.

1. **원본이 바뀐 이유를 먼저 확인한다** — 프로토타입에도 따라야 하는 변화인지, 프로토타입에서
   필요 없는 것인지.
2. 따라야 한다면 프로토타입(`Jeju-subsidence-AI/tools/`)에 같은 내용을 옮긴다.
3. 그다음 이 폴더의 기대 diff를 갱신한다.

```sh
cd projects/jeju-ai/apps/jeju-subsidence-ai
git fetch origin && git checkout develop && git pull
cd -
for f in gislib.py build_data.py run_index.py geocode_excavation.py; do
  diff -u --label "a/tools/$f" --label "b/pipeline/$f" \\
    "projects/jeju-ai/apps/jeju-subsidence-ai/tools/$f" \\
    "projects/jeju-ai/apps/jeju-ai-saas-be/pipeline/$f" \\
    > "scripts/jeju-ai-parity/expected/$f.diff"
done
```

기대를 갱신할 때는 **왜 바뀌었는지**를 커밋 메시지에 적는다 — 기대 diff 는 사람이 읽는 파일이다.
