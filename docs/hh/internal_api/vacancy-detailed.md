## `/vacancy/{id}` (front internal API, подробная страница вакансии)

### Назначение

**Внутренний фронтовый эндпоинт карточки вакансии.**

Используется фронтом hh.ru на странице просмотра конкретной вакансии, возвращает **большой JSON cо всеми данными для рендера страницы**:

- основная информация о вакансии (`vacancyView`);
- статус отклика текущего соискателя и краткий сниппет (`applicantVacancyResponseStatuses.shortVacancy`);
- данные об аккаунте/резюме пользователя, таргетинг, уведомления;
- меню, подвал, TRL, конфиги микрофронтов, баннеры, аналитика и пр.

Как и `/search/vacancy`, это **внутренний** контракт, без гарантий стабильности.

---

### HTTP‑запрос

- **Метод**: `GET`
- **URL**: `https://{region}.hh.ru/vacancy/{vacancyId}`
  - пример: `https://krasnoyarsk.hh.ru/vacancy/128593772`.
- **Формат ответа**: JSON (`Accept: application/json`).
- Как правило, браузер/SPA ходит сюда **с теми же куками и xsrf‑токеном**, что и к `/search/vacancy`.

---

### Структура ответа (верхний уровень)

Ответ — **единый объект**. Ключевые блоки:

- `topLevelSite`, `registrationSiteId`, `topLevelDomain`, `logos` — базовая инфа о площадке.
- `banners` — рекламные слоты для страницы вакансии (правый столбец, рекомендации, тизеры и т.п.).
- `authUrl` — URL‑ы и формы логина/регистрации/восстановления для сценария отклика.
- `applicantInfo`, `resumeLimits` — агрегированная инфа по резюме пользователя.
- `userTargeting` — таргетинговый профиль соискателя (puid‑поля).
- `userNotifications` — список уведомлений.
- `articleRewriteRoutes` — список служебных маршрутов для подмены статей.
- `headerMenu`, `footer`, `socialNetworksLinks` — навигация, подвал, соцсети.
- `currencies` — валюты и курсы.
- `vacancyInternalInfo` — внутренние метаданные по вакансии (для работодателя/модерации).
- `applicantVacancyResponseStatuses` — состояние отклика текущего пользователя по этой вакансии + короткий вид вакансии.
- `chatBot` — конфигурация чат‑бота рекомендаций.
- `vacancyView` — **основной блок карточки вакансии** (детальное описание).
- `adsVacancyParams`, `counters` — аналитика/рекламные параметры.
- `session`, `displayType`, `langs`, `trl`, `features`, `experiments` — окружение страницы и фичфлаги.
- `request`, `locale`, `config`, `sharedRemoteEntry`, `microFrontends` — тех. окружение фронта.

Ниже подробнее только по критичным для карточки блокам: `vacancyView`, `applicantVacancyResponseStatuses` и `vacancyInternalInfo`. Остальные по смыслу почти полностью совпадают с уже описанными для `/search/vacancy`.

---

### Блок `vacancyView` — основная карточка вакансии

`vacancyView` — это **детальная модель вакансии**, которую использует страница `/vacancy/{id}`.

Основные поля (по примеру `128593772`):

- **Идентификация и статус**:
  - `vacancyId` — id вакансии.
  - `managerId` — id менеджера работодателя, ответственного за вакансию.
  - `approved` — прошла ли модерацию hh.
  - `status` — объект с флагами:
    - `active`, `archived`, `disabled`, `waiting`, `needFix` — состояние публикации / модерации.
  - `isBrandingPreview` — режим предпросмотра брендирования.
  - `multi` — признак объединённой вакансии (multi‑vacancy).
  - `canApplyAiAssistant` — можно ли включить ИИ‑помощника по найму.

- **Общие сведения**:
  - `name` — название вакансии.
  - `publicationDate` — ISO‑дата публикации.
  - `validThroughTime` — ISO‑дата окончания размещения.

- **Оплата (`compensation`)**:
  - структура совпадает с моделью из поиска:
    - `noCompensation: {}` — зарплата не указана;
    - либо поля `from`, `to`, `currency`, `mode`, `frequency` и т.п. (в вашем примере только `noCompensation`).

- **Компания (`company`)**:
  - `@showSimilarVacancies` — можно ли показывать блок похожих вакансий работодателя.
  - `@trusted` — флаг «проверенный работодатель».
  - `@category` — тип (`COMPANY`, `PROJECT_DIRECTOR` и т.п.).
  - `@countryId`, `@state` — страна и статус модерации.
  - `id`, `name`, `visibleName` — идентификаторы и отображаемое имя.
  - `employerOrganizationFormId`, `showOrganizationForm` — отображение орг‑формы.
  - `companySiteUrl` — сайт компании.
  - `accreditedITEmployer` — IT‑аккредитация.
  - `isIdentifiedByEsia` — прошла ли компания идентификацию через Госуслуги.

- **Регион и адрес**:
  - `area`:
    - `@id` — id города/региона;
    - `@regionId`, `@countryIsoCode` — регион и страна;
    - `name` — название города;
    - `path` — путь в дереве регионов;
    - `regionName`, `areaNamePre`, `areaCatalogTitle` — тексты для UI/SEO.
  - `address`:
    - в примере только `mapData: null`, `metroStations: null` (для удалёнки часто адрес минимален).

- **Контакты работодателя (`contactInfo`)**:
  - `fio` — контактное лицо.
  - `email` — e‑mail (может быть null, если нет явной почты в карточке).
  - `phones` — вложенный объект, обычно `phones.phones: [{ country, city, number }]`.
  - `callTrackingEnabled` — включён ли call‑tracking (виртуальный номер hh).
  - `asyncContactInfo` — ленивые/отложенные контакты (часто `null` или подтягиваются отдельным запросом).

- **Флаги и вспомогательные поля**:
  - `@showContact` — можно ли показывать контакты.
  - `allowChatWithManager` — доступен ли чат с менеджером.
  - `@workSchedule` — агрегированный код расписания (например, `remote`).
  - `@acceptHandicapped` — доступна ли вакансия соискателям с инвалидностью.
  - `@ageRestriction` — возрастные ограничения (если есть).
  - `insider` — данные виджета «Инсайдер» (описание жизни в компании), в примере `null`.

- **Опыт и занятость**:
  - `workExperience` — код опыта (`between3And6`, `noExperience`, и т.п.).
  - `employment` — объект с типом:
    - `@type` — `PROJECT`, `FULL`, `PART`, `PROBATION`, `VOLUNTEER` и пр.
  - `employmentForm` — форма оформления (`PROJECT`, `FULL`, и др.).

- **Формат работы / график / часы**:
  - `workScheduleByDays` — массив кодов графика по дням (`SIX_ON_ONE_OFF`, `FIVE_ON_TWO_OFF`, …).
  - `workingHours` — массив кодов длительности (`FLEXIBLE`, `HOURS_8` и т.п.).
  - `workFormats` — массив форматов (`REMOTE`, `ON_SITE`, `HYBRID`, `FIELD_WORK`).
  - `flyInFlyOutDurations` — список длительностей вахты (пустой массив, если не вахта).
  - `nightShifts` — есть ли ночные смены.
  - `internship` — является ли вакансия стажировкой.

- **Описание и навыки**:
  - `description` — HTML‑описание вакансии (обязанности, требования, условия и т.д.).
  - `keySkills.keySkill` — массив строк‑навыков (в примере: `"Python"`, `"FastAPI"`, `"PostgreSQL"` и т.п.).
  - `driverLicenseTypes` — список категорий прав (может быть `null` или массив строк).

- **Дополнительные настройки UI**:
  - `mapDisabled` — отключена ли карта.
  - `showSignupForm`, `showResumeForm` — нужно ли показывать формы регистрации/создания резюме.
  - `showSkillsSurvey` / `skillsSurveyProfession` — опросы по навыкам.
  - `vacancyConstructorTemplate` — шаблон конструктора вакансий (если используется).
  - `branding`, `brandingType`, `brandSnippetExpirationTime` — данные брендирования.
  - `systemInfo` — низкоуровневая служебная информация.

- **Права и фичи**:
  - `canViewResponses` — можно ли просматривать отклики (для работодателя).
  - `userTestId` — id теста, связанного с вакансией (если есть).
  - `userLabels` — массив пользовательских меток для вакансии.
  - `features` — массив фич, например `"canApply"`, `"canComplain"`.
  - `vacancyOnMapLink` — относительный URL поиска вакансий на карте.
  - `confirmableKeySkills.providers` — провайдеры подтверждаемых навыков.
  - `professionalRoleIds` — список id проф. ролей (в примере `[96]`).
  - `translations` — человекочитаемые строки:
    - `workExperience` — например, `"3–6 лет"`;
    - `employment` — `"Проектная работа"` и т.п.

- **Свойства вакансии (`vacancyProperties`)** — те же, что и в поиске:
  - `properties` — массив объектов с параметрами тарифов/услуг:
    - `id`, `propertyType` (`HH_STANDARD`, `HH_CLICKME_BOOST`, `HH_RESUME_GIFTS`, `HH_SEARCH_RESULTS_NORMAL_POSITION` и др.);
    - `bundle` — пакет (обычно `"HH"`);
    - `propertyWeight` — вес;
    - `parameters` — пары `{ key, value }` (`packageName`, `serviceId`, `giftsCount` и др.);
    - `startTimeIso`, `endTimeIso` — период действия.
  - `calculatedStates.HH` — сводка по тарифу:
    - `advertising`, `anonymous`, `premium`, `standardPlus`, `standard` и др.;
    - `filteredPropertyNames` — какие propertyType реально учитываются;
    - `translationKeys` — ключи TRL для отображения типа публикации.

---

### Блок `applicantVacancyResponseStatuses`

`applicantVacancyResponseStatuses` — объект, индексированный по `vacancyId` в виде строки. Для каждой вакансии содержит **состояние отклика текущего соискателя** и «короткую» версию вакансии.

Структура для `"128593772"`:

- `test.hasTests` — есть ли тесты для отклика.
- `negotiations` — состояние переговоров:
  - `topicList` — список тредов/тем (в примере пустой).
  - `total` — количество тем.
  - `readOnlyInterval` — окно read‑only по откликам (например, 180 дней).
  - `untrustedEmployerRestrictionsApplied` — флаг ограничений по неблагонадёжным работодателям.
- `by_country_applicant_visibility` — ограничения видимости резюме по странам:
  - `responseAllowed` — можно ли откликаться в текущей конфигурации.
  - `visibleForCommonCountriesEnableRequired` — нужно ли включать видимость для общих стран.
  - `visibleForUzbekistanEnableRequired` — нужно ли включать видимость для Узбекистана.
- `letterMaxLength` — максимальная длина сопроводительного письма.
- `shortVacancy` — **короткий сниппет вакансии**, структура почти 1:1 с элементом массива `vacancies` в `/search/vacancy`:
  - атрибуты: `@workSchedule`, `@showContact`, `@responseLetterRequired`.
  - основные поля: `vacancyId`, `name`, `company`, `compensation`, `publicationTime`, `area`, `acceptTemporary`, `creationSite`, `displayHost` и т.д.
  - коммуникации: `inboxPossibility`, `chatWritePossibility`, `notify`.
  - `links.desktop` / `links.mobile` — URL’ы карточки.
  - `acceptIncompleteResumes`, массивы `driverLicenseTypes`, `languages`, `workingDays`, `workingTimeIntervals`, `workingTimeModes`.
  - `vacancyProperties` + `calculatedStates` — тарифные свойства, аналогичные `vacancyView.vacancyProperties`.
  - `vacancyPlatforms`, `professionalRoleIds`, `workExperience`, `employment`, `employmentForm`, `workFormats`, `workScheduleByDays`, `workingHours`, `experimentalModes` и др.
  - флаги по контракту: `acceptLaborContract`, `civilLawContracts`, `autoResponse.acceptAutoResponse` и пр.

Этот блок обычно используется для **индикации статуса отклика**, отображения бейджей «Вы откликнулись / Вас пригласили» и быстрого показа сниппета без повторной загрузки полной `vacancyView`.

---

### Блок `vacancyInternalInfo`

Внутренняя техническая/модерационная информация по вакансии, используется в основном в инструментах работодателя.

Поля (по примеру):

- `vacancyId` — id вакансии.
- `vacancyPremoderateStatus` — статус премодерации (`APPROVED`, `NEED_FIX`, и др.).
- `approved` — булевый флаг «одобрено».
- `canChangeClosureStatus` — можно ли менять статус закрытия.
- `canBeProlongated` — можно ли продлевать.
- `canBeArchived` — можно ли отправить в архив.
- `userTestId` — связанный тест (если есть).
- `ownerEmployerManagerId` — id менеджера‑владельца.
- `ownerEmployerManagerHhid` — hhid владельца.
- `daysBeingPublic` — сколько дней в активной публикации (может быть `null`).
- `freeRestoreDays` — сколько дней доступно бесплатное восстановление из архива.

---

### Прочие поля

Остальные блоки (`headerMenu`, `footer`, `trl`, `experiments`, `analyticsParams`, `counters`, `microFrontends` и т.д.) совпадают по смыслу со структурой, задокументированной для `/search/vacancy` и представляют собой **страничное окружение**:

- навигация, подвал и сервисные ссылки;
- настройки языка/локали и словари переводов;
- подключения микрофронтов (эмбедды чатов, отзывов, карьеры и т.п.);
- аналитика и рекламные параметры.

Для прикладной логики карточки вакансии обычно достаточно ориентироваться на **`vacancyView` и `applicantVacancyResponseStatuses`**; остальные блоки важны при работе с фронтом и интеграции виджетов/аналитики.