# Источники

[Навигация](README.md).

## Предметное моделирование

| Источник | Тема |
| --- | --- |
| Eric Evans, [Domain-Driven Design Reference](https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf), 2015 | Терминология, язык, контексты, сущности, сервисы, фабрики и отношения моделей |
| Martin Fowler, [Bounded Context](https://martinfowler.com/bliki/BoundedContext.html) | Границы согласованного смысла и связи контекстов |
| Martin Fowler, [DDD Aggregate](https://martinfowler.com/bliki/DDD_Aggregate.html) | Корень и граница агрегата |
| Martin Fowler, [Value Object](https://martinfowler.com/bliki/ValueObject.html) | Равенство значений и неизменяемое представление |
| Edward Hieatt и Rob Mee, [Repository](https://martinfowler.com/eaaCatalog/repository.html) | Абстракция доступа к предметным объектам |
| Randy Stafford, [Service Layer](https://martinfowler.com/eaaCatalog/serviceLayer.html) | Координация операций на границе приложения |
| Martin Fowler, [CQRS](https://martinfowler.com/bliki/CQRS.html) | Разделение моделей чтения и изменения, условия и стоимость применения |
| Martin Fowler, [Domain Event](https://martinfowler.com/eaaDev/DomainEvent.html) (черновик) | Факт и время события |

## Laravel

Ссылки ведут на документацию Laravel 13.x. Для другой версии используйте соответствующий раздел документации.

| Документация | Механизм |
| --- | --- |
| [Service Providers](https://laravel.com/docs/13.x/providers) | Сборка и регистрация компонентов |
| [Service Container](https://laravel.com/docs/13.x/container) | Привязка контрактов, время жизни |
| [Database](https://laravel.com/docs/13.x/database) | Транзакции и обработка deadlock |
| [Query Builder](https://laravel.com/docs/13.x/queries) | Условные изменения и блокировки |
| [Eloquent](https://laravel.com/docs/13.x/eloquent) | Получение и сохранение записей |
| [Validation](https://laravel.com/docs/13.x/validation) | Проверка HTTP-входа и FormRequest |
| [Queues](https://laravel.com/docs/13.x/queues) | Отправка заданий после commit |
| [HTTP Client](https://laravel.com/docs/13.x/http-client) | Ожидание, повторы и подмена ответов |
| [Testing](https://laravel.com/docs/13.x/testing) | Запуск и разделение проверок |
| [Database Testing](https://laravel.com/docs/13.x/database-testing) | Окружение для проверок хранения |
| [Mocking](https://laravel.com/docs/13.x/mocking) | Подмена зависимостей и механизмов Laravel |
| [Error Handling](https://laravel.com/docs/13.x/errors) | Разделение reporting/rendering, JSON-ответы и контекст |
| [Logging](https://laravel.com/docs/13.x/logging) | Структурированные диагностические записи |
| [Configuration](https://laravel.com/docs/13.x/configuration) | Чтение и кэширование конфигурации |

## PHP

- [Visibility](https://www.php.net/manual/en/language.oop5.visibility.php) — доступ к свойствам, включая асимметричную видимость.
- [DateTimeImmutable](https://www.php.net/manual/en/datetimeimmutable.construct.php) — создание времени и тип ошибки некорректной строки.
