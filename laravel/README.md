# Профиль Laravel

[Общая навигация](../README.md). Этот профиль конкретизирует ядро для проектов на PHP и Laravel.

Роли уровней, портов и адаптеров и их взаимодействие раскрыты в [архитектурном разделе](../architecture/README.md). Он объясняет устройство изолированного ядра; здесь описаны его реализация средствами Laravel и границы допустимых упрощений.

## LAR-PROFILE-01

**Базовый выбор профиля — изолированная доменная модель и явные прикладные сценарии.**

Основания: [ARCH-FIT-01](../core/principles.md#arch-fit-01), [ARCH-DEP-01](../core/boundaries.md#arch-dep-01), [ARCH-DEC-01](../core/principles.md#arch-dec-01).

После принятия профиля действуют следующие соглашения:

- Domain — PHP-модель без зависимостей от Laravel и ORM.
- Application — сценарии, входные и выходные данные, прикладные порты; без фасадов и запросов к ORM.
- Infrastructure — реализации портов, хранилище, HTTP-клиенты и технические механизмы.
- Presentation — HTTP, CLI и входящие задания очереди.
- Providers — сборка зависимостей и подключение модуля к Laravel.

Это выбранный вариант реализации. Для простого справочного CRUD проект может принять Eloquent непосредственно в прикладном сценарии и зафиксировать область такого упрощения в [ADR](../templates/architecture-decision.md). Смешение вариантов внутри одного сценария требует объяснения. Наличие Eloquent в проекте не определяет наличие или отсутствие DDD.

## Порядок применения

1. Пройдите [workflow ядра](../core/workflow.md): термины, контексты, правила и согласованность.
2. Зафиксируйте принятие профиля и его область действия в документации проекта.
3. Выберите [структуру и расположение файлов](structure.md#раскладка-сквозного-примера), реализуйте [модель](domain-model.md) и [сценарий](application.md).
4. Добавьте нужные [адаптеры](persistence.md) и [точки входа](presentation.md).
5. Используйте [сквозной пример](example.md) для сопоставления компонентов.
6. Выполните [проверки](testing.md) и оцените реализацию по [критериям профиля](review-criteria.md).
7. Проверьте значимые для сценария [настройки, диагностику и автоматизацию](operations.md).

Классы и каталоги добавляются по потребности. Например, сценарий внешнего поиска может обходиться без агрегата, ORM и транзакции.

## Версии и техническая документация

Примеры используют API Laravel 13.x. При переносе сверяйте механизмы и регистрацию компонентов с версией из `composer.lock` целевого проекта. Версию PHP определяют зависимости этого проекта.

Требования для подключения сквозного примера перечислены в [его документе](example.md#границы-примера).

## Карта решений

| Решение профиля | Основания ядра |
| --- | --- |
| [Структура модулей](structure.md#lar-struct-01) | [DDD-CTX-01](../core/strategic-design.md#ddd-ctx-01), [ARCH-DEP-01](../core/boundaries.md#arch-dep-01) |
| [PHP-модель](domain-model.md#lar-model-01) | [DDD-ENTITY-01](../core/domain-model.md#ddd-entity-01), [DDD-VO-01](../core/domain-model.md#ddd-vo-01), [DDD-INV-01](../core/domain-model.md#ddd-inv-01) |
| [Прикладной сценарий](application.md#lar-use-01) | [ARCH-USE-01](../core/application.md#arch-use-01), [ARCH-CONTRACT-01](../core/boundaries.md#arch-contract-01) |
| [Сборка зависимостей](application.md#lar-di-01) | [ARCH-COMPOSE-01](../core/boundaries.md#arch-compose-01) |
| [Транзакции](application.md#lar-tx-01) | [ARCH-CONS-01](../core/application.md#arch-cons-01) |
| [Внешние эффекты](application.md#lar-effect-01) | [DDD-EVENT-01](../core/domain-model.md#ddd-event-01), [ARCH-EFFECT-01](../core/application.md#arch-effect-01) |
| [Хранение модели](persistence.md#lar-persist-01) | [DDD-REPO-01](../core/domain-model.md#ddd-repo-01), [DDD-FACT-01](../core/domain-model.md#ddd-fact-01) |
| [Конкурирующие изменения](persistence.md#lar-lock-01) | [ARCH-CONS-01](../core/application.md#arch-cons-01) |
| [Внешний API](persistence.md#lar-remote-01) | [DDD-ACL-01](../core/strategic-design.md#ddd-acl-01), [ARCH-FAIL-01](../core/boundaries.md#arch-fail-01) |
| [Кэш](persistence.md#lar-cache-01) | [ARCH-CACHE-01](../core/application.md#arch-cache-01) |
| [Точки входа](presentation.md#lar-entry-01) | [ARCH-CONTRACT-01](../core/boundaries.md#arch-contract-01) |
| [Ошибки](presentation.md#lar-error-01) | [ARCH-FAIL-01](../core/boundaries.md#arch-fail-01) |
| [Задания очереди](presentation.md#lar-queue-01) | [ARCH-USE-01](../core/application.md#arch-use-01), [ARCH-EFFECT-01](../core/application.md#arch-effect-01) |
| [Тестирование](testing.md#lar-test-01) | [TEST-BEH-01](../core/testing.md#test-beh-01), [TEST-USE-01](../core/testing.md#test-use-01) |
| [Согласование валидации](presentation.md#lar-valid-01) | [ARCH-NORM-01](../core/boundaries.md#arch-norm-01), [TEST-CONTRACT-01](../core/testing.md#test-contract-01) |
| [HTTP-семантика](presentation.md#lar-proto-01) | [ARCH-CONTRACT-01](../core/boundaries.md#arch-contract-01), [TEST-CONTRACT-01](../core/testing.md#test-contract-01) |
| [Настройки и пределы ожидания](operations.md#lar-config-01) | [ARCH-COMPOSE-01](../core/boundaries.md#arch-compose-01), [ARCH-BUDGET-01](../core/boundaries.md#arch-budget-01) |
| [Диагностика](operations.md#lar-obs-01) | [ARCH-OBS-01](../core/boundaries.md#arch-obs-01) |
| [Команды и CI](operations.md#lar-ci-01) | [TEST-ARCH-01](../core/testing.md#test-arch-01), [TEST-CONTRACT-01](../core/testing.md#test-contract-01) |
