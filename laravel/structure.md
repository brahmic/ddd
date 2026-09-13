# Структура модулей

[Профиль](README.md).

## LAR-STRUCT-01

Основания: [DDD-CTX-01](../core/strategic-design.md#ddd-ctx-01), [ARCH-DEP-01](../core/boundaries.md#arch-dep-01).

**Решение профиля:** группировать код по предметным модулям. Модуль может реализовывать контекст или часть контекста; соответствие фиксируется в его README.

## Раскладка сквозного примера

В [примере отмены](example.md) модуль `Booking` реализует контекст бронирования. Внутри него отдельно видны агрегат, прикладной сценарий, выходные порты и адаптеры. Файлы в целевом приложении можно разместить так:

```text
.
├── app/Modules/Booking/
│   ├── README.md
│   ├── Domain/
│   │   └── Aggregates/
│   │       └── Booking/
│   │           ├── Booking.php
│   │           ├── BookingId.php
│   │           ├── BookingState.php
│   │           ├── CannotCancelBooking.php
│   │           └── CannotCreateBooking.php
│   ├── Application/
│   │   ├── UseCases/
│   │   │   └── CancelBooking/
│   │   │       ├── CancelBooking.php
│   │   │       ├── CancelBookingResult.php
│   │   │       ├── BookingNotFound.php
│   │   │       └── BookingAccessDenied.php
│   │   └── Ports/
│   │       ├── Persistence/
│   │       │   ├── BookingStore.php
│   │       │   ├── LoadedBooking.php
│   │       │   ├── BookingConflict.php
│   │       │   ├── BookingStorageUnavailable.php
│   │       │   ├── BookingDataInvalid.php
│   │       │   └── Transaction.php
│   │       └── Time/
│   │           └── Clock.php
│   ├── Infrastructure/
│   │   ├── Persistence/
│   │   │   └── Database/
│   │   │       ├── DatabaseBookingStore.php
│   │   │       └── LaravelTransaction.php
│   │   └── Time/
│   │       └── SystemClock.php
│   ├── Presentation/
│   │   └── Http/
│   │       └── Controllers/
│   │           └── CancelBookingController.php
│   └── Providers/
│       └── BookingServiceProvider.php
├── bootstrap/providers.php
├── routes/web.php
├── database/migrations/
│   └── ..._create_bookings_table.php
└── tests/
    ├── Unit/Booking/
    │   ├── Domain/
    │   │   └── BookingTest.php
    │   └── Application/
    │       └── CancelBookingTest.php
    └── Feature/Booking/
        ├── Persistence/
        │   └── DatabaseBookingStoreTest.php
        └── Http/
            └── CancelBookingHttpTest.php
```

### Как читать границы

| Каталог внутри модуля | Ответственность |
| --- | --- |
| `Domain/Aggregates/Booking` | Корень `Booking`, его идентификатор, состояние и предметные отказы. Здесь защищаются инварианты одной брони |
| `Application/UseCases/CancelBooking` | Сценарий отмены, его выходной DTO и отказы доступа или обязательной загрузки |
| `Application/Ports/Persistence` | Потребность сценариев в хранении и транзакции: интерфейсы, загруженная модель с версией и ошибки этой границы |
| `Application/Ports/Time` | Контракт получения текущего времени |
| `Infrastructure/Persistence/Database` | Реализации хранения и транзакции на одном соединении Laravel |
| `Infrastructure/Time` | Реализация часов |
| `Presentation/Http/Controllers` | Преобразование HTTP-запроса в вызов сценария и его результата в ответ |
| `Providers` | Сборка портов и адаптеров, подключение модуля |

`CannotCancelBooking` принадлежит агрегату: это отказ предметного перехода. `BookingAccessDenied` принадлежит сценарию: это отказ действующему лицу. `BookingConflict` принадлежит порту хранения: это результат проверки версии при записи. Размещение отражает владельца правила или контракта.

Каталог агрегата объединяет его корень и обслуживающие его типы. `BookingId` — объект-значение, `BookingState` — представление состояния; они остаются рядом с `Booking`, потому что меняются вместе с его моделью. По мере появления других агрегатов у каждого будет собственный каталог и граница изменения.

Классы приведены в сквозном примере и [реализации транзакции](application.md#lar-tx-01). Каждый класс, интерфейс и enum помещается в одноимённый файл. Например, `App\Modules\Booking\Application\UseCases\CancelBooking\CancelBooking` соответствует `app/Modules/Booking/Application/UseCases/CancelBooking/CancelBooking.php` при привязке `App\\` к `app/` в `composer.json`; это сопоставление [PSR-4 в Composer](https://getcomposer.org/doc/04-schema.md#psr-4). Имена и импорты фрагментов соответствуют дереву.

Маршрут, миграцию и тесты добавьте в целевом проекте по [границам примера](example.md#границы-примера) и [проверкам профиля](testing.md). В этой раскладке выбран HTTP-маршрут с сессионной аутентификацией в `routes/web.php`; при использовании API разместите его в подключённом файле API-маршрутов с аутентификацией проекта. В `bootstrap/providers.php` добавьте `BookingServiceProvider`, в README модуля опишите его язык, публичные сценарии и зависимости.

Для одного модуля допустим `app/Booking/` с соответствующим пространством имён. Новый сценарий получает соседний каталог в `UseCases`; общий для нескольких сценариев порт остаётся в `Ports`. Предметные политики и события размещаются рядом с моделью, которой принадлежат. `Presentation/Console` и `Presentation/Jobs` добавляются при появлении соответствующих точек входа. Сохраняйте существующую структуру проекта, если она уже выражает эти границы.

## Направления зависимостей

| Компонент | Допустимые зависимости в этом профиле |
| --- | --- |
| Domain | Стандартные средства PHP, собственные доменные типы и контракты |
| Application | Domain, собственные DTO и порты |
| Infrastructure | Domain, прикладные порты, Laravel и технические библиотеки |
| Presentation | Application, Laravel; доменные типы ошибок при переводе исходов |
| Providers | Все части модуля для сборки |

Это направления зависимостей исходного кода. При выполнении сценарий вызывает инфраструктурную реализацию через внутренний контракт.

Контроллер получает результат сценария, а не Eloquent Model. Обработчик ошибок может знать тип доменного отказа. Запрет всех импортов Domain в Presentation был бы сильнее принятого здесь соглашения.

## Подключение модуля

Service Provider размещается внутри модуля. В `register()` связываются контракты с реализациями; в `boot()` подключаются маршруты и другие механизмы. В Laravel 13 пользовательские провайдеры регистрируются через `bootstrap/providers.php`. См. [Service Providers](https://laravel.com/docs/13.x/providers).

Локальные маршруты, миграции и конфигурация удобны для самостоятельного модуля. Допустимо хранить их в общих каталогах проекта, если принадлежность и регистрация остаются понятными.

## Взаимодействие модулей

Обращайтесь через публичный прикладной контракт либо согласованное сообщение. Не загружайте Eloquent-модели другого контекста напрямую и не создавайте общий доменный объект только ради одинаковых полей.

В показанной раскладке модуль явно объявляет доступные другим контекстам сценарии и DTO из `Application/UseCases` в своём README. `Domain/Aggregates`, выходные `Application/Ports` и `Infrastructure` остаются его внутренними деталями. PHP-пространство имён само по себе этот доступ не ограничивает; договорённость проверяется анализом зависимостей по [LAR-TEST-03](testing.md#lar-test-03).

Для Shared Kernel укажите владельцев и порядок совместных изменений по [DDD-MAP-01](../core/strategic-design.md#ddd-map-01).

**Проверка:** README модуля описывает язык, публичный контракт, зависимости и принятые решения. Тесты и анализ импортов проверяют указанную таблицу.
