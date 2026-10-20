# inp-devops

Innopam 작업 공간. 클러스터 운영 저장소와 제품 저장소를 서브모듈로 묶어 한곳에서 본다.
실제 내용은 각 서브모듈에 있고, 이 저장소는 그것들을 어느 커밋에서 함께 보는지만 기록한다.

- `ops/dev0` → innopam/dev0 (dev0 클러스터 운영)
- `projects/inp/official-website` → innopam/official-website (회사 홈페이지, Next.js)
- `projects/jeju-ai/apps/jeju-ai-saas-be` → innopam/jeju-ai-saas-be (제주 지반침하 SaaS 서버)
- `projects/jeju-ai/apps/jeju-ai-saas-fe` → innopam/jeju-ai-saas-fe (제주 지반침하 SaaS 화면, React)
- `projects/jeju-ai/repos/gis-sass` → innopam/gis-sass (GIS 제품)
- `projects/jeju-ai/repos/jeju-subsidence-ai` → innopam/Jeju-subsidence-AI (제주 지반침하 프로토타입)

받기:

```sh
git clone --recurse-submodules git@github.com:garam-park/inp-devops.git
# 권한 있는 서브모듈만 받을 때
git submodule update --init ops/dev0
```

커밋 훅(markdownlint) 걸기, 처음 한 번:

```sh
mise trust && mise install && mise exec -- lefthook install
```

규칙은 `AGENTS.md`.
