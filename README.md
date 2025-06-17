| HTTP Method | URL                     | 기능          | 렌더링할 템플릿 (HTML 파일)          |
| ----------- | ----------------------- | ----------- | --------------------------- |
| GET         | `/issue/new`           | 새 이슈 생성 폼   | `issue/form.html`           |
| POST        | `/issue`               | 새 이슈 생성 처리  | (성공 시 리다이렉트 or 메시지, 템플릿 없음) |
| GET         | `/issue`               | 이슈 목록 조회    | `issue/list.html`           |
| GET         | `/issue/<id>`          | 이슈 상세 조회    | `issue/detail.html`         |
| GET         | `/issue/<id>/edit`     | 이슈 수정 폼     | `issue/edit.html`           |
| POST        | `/issue/<id>/edit`     | 이슈 수정 처리    | (성공 시 리다이렉트 or 메시지, 템플릿 없음) |
| POST        | `/issue/<id>/delete`   | 이슈 삭제 처리    | (성공 시 리다이렉트 or 메시지, 템플릿 없음) |