# inp-devops

Innopam 작업 공간. 클러스터 운영 저장소와 제품 저장소를 서브모듈로 묶어 한곳에서 본다.
실제 내용은 각 서브모듈에 있고, 이 저장소는 그것들을 어느 커밋에서 함께 보는지만 기록한다.

- `ops/dev0` → innopam/dev0 (dev0 클러스터 운영)
- `projects/gis-sass` → innopam/gis-sass (GIS 제품)

받기:

```sh
git clone --recurse-submodules git@github.com:garam-park/inp-devops.git
# 권한 있는 서브모듈만 받을 때
git submodule update --init ops/dev0
```

규칙은 `AGENTS.md`.
