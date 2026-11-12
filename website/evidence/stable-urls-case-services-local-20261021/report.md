# 稳定网址与案例服务入口：本地验收

日期：2026-10-21。本地候选 `cc132dc0e7da5cecf41d`，尚未发布。生产版本仍按上次回执为 `4bc544a5361e14236d53`；本轮未连接服务器，搜索提交和外发均为 0。

## 修改范围

- 构建停止向 HTML 导航附加 `pv`；访问旧链接时，浏览器用 replaceState 清理当前地址、同站返回来源和导航链接中的旧 `pv`。不增加后退步骤。
- 保留资源缓存版本 `?v`，以及 `from`、`project`、`q`、`category`、`return` 和锚点等必要阅读状态。中英文首页目录路径也兼容。
- P09、P10 的中英文案例页增加永久库存核对与流程自动化服务链接；P36 的中英文案例页增加企业知识库搭建服务链接。复用已有咨询区和 text-link 样式。
- 内容日期指纹排除导航控制器的缓存哈希。迁移前逐页核对旧指纹；仅新增链接的 6 个案例页日期更新至 2026-10-21，其余 288 个索引页日期不变。
- 除导航控制器外，31 个既有 JS/CSS 公网文件逐字节一致；未修改视觉和动效代码，没有新增毛玻璃。

## 验收结果

- 构建通过；不提供更新日期的普通重复构建也通过，日期未被构建时间刷新。
- 296 页本地 HTTP、内部文件链接、片段锚点、单 H1 和隐私边界检查通过。
- 148 对语言页面、296 份独立标题及摘要、294 个规范网址与结构化数据检查通过。
- 5 套导航回归检查覆盖旧参数、嵌套返回来源、子目录部署、同站与同语言边界、外站链接、媒体参数、BFCache、筛选和相关案例链。
- 实际浏览器：首页案例→相关案例→返回原卡片；服务→案例→相关案例→返回服务原位置；文章→案例→返回原文章，均通过。
- 英文项目库分类和搜索→案例→相关案例→返回，保留搜索词、分类和原案例焦点。
- 中英文语言切换、案例服务入口→对应服务→咨询联系区通过。未点击电话或邮箱外联，未发送消息。
- 6 个双语案例页逐页检查：中文 360px、英文 390px，新增入口正常换行，无横向溢出。这里只是浏览器模拟，不代表真机测试。

快速导航验收中记录到两条原生 View Transition 的 InvalidStateError（Page already revealed）。对应页面和返回链正常通过；既有动画代码未改。本轮不据此声称控制台完全无错误，也不扩大到动效修正。

## 预览

- [库存案例](http://127.0.0.1:4178/cases/p10.html#case-contact-title)
- [知识库案例](http://127.0.0.1:4178/cases/p36.html#case-contact-title)
- [English](http://127.0.0.1:4178/en/cases/p36.html#case-contact-title)

验收原件：receipt.json、scope-checks.json、browser-steps.json、mobile-final.json、navigation-regressions.json、static-checks.json、seo.json、localization.json、source-diff.patch。截图：desktop-case-service.png、mobile-zh-inventory-service.png、mobile-en-knowledge-service.png。
