# Пример: отмена бронирования

[Профиль](README.md). Бизнес-условия и таблица исходов находятся в [примере ядра](../core/workflow.md#сквозной-пример-отмена-бронирования).

Пример показывает один сценарий изменения существующей брони. Возврат денег и доставка уведомлений в него не входят. Все PHP-блоки ниже — отдельные фрагменты файлов. Несколько классов собраны в блоке для чтения; в приложении разнесите их по файлам согласно [раскладке модуля](structure.md#раскладка-сквозного-примера).

Фрагменты используют возможности PHP 8.3+, включая `DateMalformedStringException`. Совместимость всего приложения определяется его зависимостями. Поведение разбора даты описано в [PHP: DateTimeImmutable](https://www.php.net/manual/en/datetimeimmutable.construct.php).

## Модель

Основания: [DDD-ENTITY-01](../core/domain-model.md#ddd-entity-01), [DDD-VO-01](../core/domain-model.md#ddd-vo-01), [DDD-INV-01](../core/domain-model.md#ddd-inv-01), [DDD-FACT-01](../core/domain-model.md#ddd-fact-01).

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Domain\Aggregates\Booking;

use DateTimeImmutable;
use DomainException;
use InvalidArgumentException;

final readonly class BookingId
{
    public function __construct(public string $value)
    {
        if (trim($value) === '') {
            throw new InvalidArgumentException('Booking id must not be empty.');
        }
    }

    public function equals(self $other): bool
    {
        return $this->value === $other->value;
    }
}

enum BookingState: string
{
    case Confirmed = 'confirmed';
    case Cancelled = 'cancelled';
}

final class CannotCancelBooking extends DomainException {}
final class CannotCreateBooking extends DomainException {}

final class Booking
{
    private function __construct(
        private readonly BookingId $id,
        private readonly string $ownerId,
        private readonly DateTimeImmutable $startsAt,
        private BookingState $state,
    ) {
        if (trim($ownerId) === '') {
            throw new InvalidArgumentException('Owner id must not be empty.');
        }
    }

    public static function confirm(
        BookingId $id,
        string $ownerId,
        DateTimeImmutable $startsAt,
        DateTimeImmutable $now,
    ): self {
        if ($startsAt <= $now) {
            throw new CannotCreateBooking('Booking must start in the future.');
        }

        return new self($id, $ownerId, $startsAt, BookingState::Confirmed);
    }

    public static function reconstitute(
        BookingId $id,
        string $ownerId,
        DateTimeImmutable $startsAt,
        BookingState $state,
    ): self {
        return new self($id, $ownerId, $startsAt, $state);
    }

    public function id(): BookingId
    {
        return $this->id;
    }

    public function isOwnedBy(string $actorId): bool
    {
        return $this->ownerId === $actorId;
    }

    public function state(): BookingState
    {
        return $this->state;
    }

    public function cancel(DateTimeImmutable $now): bool
    {
        if ($this->state === BookingState::Cancelled) {
            return false;
        }

        if ($now >= $this->startsAt) {
            throw new CannotCancelBooking('Booking has already started.');
        }

        $this->state = BookingState::Cancelled;

        return true;
    }
}
```

Восстановление брони с началом в прошлом допустимо: существующие брони не исчезают после начала услуги. Метод создания имеет дополнительное условие примера — начало в будущем. Повтор отмены возвращает отсутствие изменения, даже если к моменту повтора услуга уже должна была начаться.

## Сценарий

Основания: [ARCH-USE-01](../core/application.md#arch-use-01), [ARCH-CONS-01](../core/application.md#arch-cons-01), [ARCH-PORT-01](../core/boundaries.md#arch-port-01).

Здесь выбран прикладной порт `BookingStore`. Он возвращает модель вместе с технической версией в `LoadedBooking`. Версия не добавляется в предметную модель. Вариант с доменным репозиторием также возможен, если его контракт соответствует потребностям проекта.

Контракты хранения, результат загрузки и ошибки этого порта находятся в `Application/Ports/Persistence`:

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Application\Ports\Persistence;

use Closure;
use App\Modules\Booking\Domain\Aggregates\Booking\Booking;
use App\Modules\Booking\Domain\Aggregates\Booking\BookingId;
use RuntimeException;

final class BookingConflict extends RuntimeException {}
final class BookingStorageUnavailable extends RuntimeException {}
final class BookingDataInvalid extends RuntimeException {}

final readonly class LoadedBooking
{
    public function __construct(
        public Booking $booking,
        public int $version,
    ) {
        if ($version < 1) {
            throw new BookingDataInvalid('Version must be positive.');
        }
    }
}

interface BookingStore
{
    public function load(BookingId $id): ?LoadedBooking;

    /** @throws BookingConflict */
    public function saveCancellation(Booking $booking, int $expectedVersion): void;
}

interface Transaction
{
    public function run(Closure $operation): mixed;
}
```

Источник времени имеет отдельный контракт в `Application/Ports/Time`:

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Application\Ports\Time;

use DateTimeImmutable;

interface Clock
{
    public function now(): DateTimeImmutable;
}
```

Сценарий, его результат и отказы доступа или обязательной загрузки находятся в `Application/UseCases/CancelBooking`:

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Application\UseCases\CancelBooking;

use App\Modules\Booking\Application\Ports\Persistence\BookingStore;
use App\Modules\Booking\Application\Ports\Persistence\Transaction;
use App\Modules\Booking\Application\Ports\Time\Clock;
use App\Modules\Booking\Domain\Aggregates\Booking\BookingId;
use RuntimeException;

final class BookingNotFound extends RuntimeException {}
final class BookingAccessDenied extends RuntimeException {}

final readonly class CancelBookingResult
{
    public function __construct(
        public string $bookingId,
        public string $state,
    ) {}
}

final readonly class CancelBooking
{
    public function __construct(
        private BookingStore $store,
        private Clock $clock,
        private Transaction $transaction,
    ) {}

    public function handle(string $bookingId, string $actorId): CancelBookingResult
    {
        return $this->transaction->run(function () use ($bookingId, $actorId) {
            $loaded = $this->store->load(new BookingId($bookingId))
                ?? throw new BookingNotFound();

            if (!$loaded->booking->isOwnedBy($actorId)) {
                throw new BookingAccessDenied();
            }

            if ($loaded->booking->cancel($this->clock->now())) {
                $this->store->saveCancellation($loaded->booking, $loaded->version);
            }

            return new CancelBookingResult(
                $loaded->booking->id()->value,
                $loaded->booking->state()->value,
            );
        });
    }
}
```

Право отмены проверено до вызова модели. Идентификатор действующего лица передаёт доверенный адаптер. `BookingConflict` сообщает о необходимости новой оценки состояния; обработчик не повторяет операцию автоматически.

## Адаптер хранения

Основания: [LAR-PERSIST-01](persistence.md#lar-persist-01), [LAR-LOCK-01](persistence.md#lar-lock-01).

Этот адаптер использует Query Builder. Для него нужна таблица `bookings`:

| Поле | Договорённость примера |
| --- | --- |
| `id` | Строковый первичный ключ |
| `owner_id` | Непустой строковый идентификатор владельца |
| `starts_at` | Момент в UTC; точность хранения согласована с приложением |
| `state` | `confirmed` или `cancelled` |
| `version` | Целое число от 1, увеличивается при каждом изменении |

Любой другой писатель этой записи также обязан соблюдать механизм версии. Метод сохраняет только отмену; он не является универсальным репозиторием создания и редактирования брони.

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Infrastructure\Persistence\Database;

use DateTimeImmutable;
use DateTimeZone;
use App\Modules\Booking\Application\Ports\Persistence\BookingConflict;
use App\Modules\Booking\Application\Ports\Persistence\BookingDataInvalid;
use App\Modules\Booking\Application\Ports\Persistence\BookingStorageUnavailable;
use App\Modules\Booking\Application\Ports\Persistence\BookingStore;
use App\Modules\Booking\Application\Ports\Persistence\LoadedBooking;
use App\Modules\Booking\Domain\Aggregates\Booking\Booking;
use App\Modules\Booking\Domain\Aggregates\Booking\BookingId;
use App\Modules\Booking\Domain\Aggregates\Booking\BookingState;
use Illuminate\Database\Connection;
use Illuminate\Database\QueryException;

final readonly class DatabaseBookingStore implements BookingStore
{
    public function __construct(private Connection $connection) {}

    public function load(BookingId $id): ?LoadedBooking
    {
        try {
            $row = $this->connection->table('bookings')
                ->where('id', $id->value)
                ->first();
        } catch (QueryException $error) {
            throw new BookingStorageUnavailable('Cannot load booking.', 0, $error);
        }

        if ($row === null) {
            return null;
        }

        try {
            return new LoadedBooking(
                Booking::reconstitute(
                    new BookingId((string) $row->id),
                    (string) $row->owner_id,
                    new DateTimeImmutable((string) $row->starts_at, new DateTimeZone('UTC')),
                    BookingState::from((string) $row->state),
                ),
                (int) $row->version,
            );
        } catch (\ValueError | \InvalidArgumentException | \DateMalformedStringException $error) {
            throw new BookingDataInvalid('Cannot restore booking.', 0, $error);
        }
    }

    public function saveCancellation(Booking $booking, int $expectedVersion): void
    {
        if ($booking->state() !== BookingState::Cancelled) {
            throw new \LogicException('Only a cancellation can be saved here.');
        }

        try {
            $updated = $this->connection->table('bookings')
                ->where('id', $booking->id()->value)
                ->where('version', $expectedVersion)
                ->update([
                    'state' => $booking->state()->value,
                    'version' => $expectedVersion + 1,
                ]);
        } catch (QueryException $error) {
            throw new BookingStorageUnavailable('Cannot save booking.', 0, $error);
        }

        if ($updated !== 1) {
            throw new BookingConflict();
        }
    }
}
```

Условное обновление проверяет версию в самой БД. Исчезновение записи после загрузки также возвращает конфликт этого сценария. При необходимости потребитель может заново загрузить состояние и определить более точный исход. Технический механизм обновления описан в [Laravel Query Builder](https://laravel.com/docs/13.x/queries#update-statements).

Адаптер предполагает корректные типы и ограничения таблицы. Для свободного внешнего JSON нужен более строгий перевод и проверка структуры до создания модели.

## Сборка

Основания: [LAR-DI-01](application.md#lar-di-01), [LAR-TX-01](application.md#lar-tx-01).

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Infrastructure\Time;

use DateTimeImmutable;
use DateTimeZone;
use App\Modules\Booking\Application\Ports\Time\Clock;

final class SystemClock implements Clock
{
    public function now(): DateTimeImmutable
    {
        return new DateTimeImmutable('now', new DateTimeZone('UTC'));
    }
}
```

Для транзакции используется `LaravelTransaction` из [документа о сценариях](application.md#lar-tx-01).

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Providers;

use App\Modules\Booking\Application\Ports\Persistence\BookingStore;
use App\Modules\Booking\Application\Ports\Persistence\Transaction;
use App\Modules\Booking\Application\Ports\Time\Clock;
use App\Modules\Booking\Infrastructure\Persistence\Database\DatabaseBookingStore;
use App\Modules\Booking\Infrastructure\Persistence\Database\LaravelTransaction;
use App\Modules\Booking\Infrastructure\Time\SystemClock;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\ServiceProvider;

final class BookingServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(Clock::class, SystemClock::class);
        $this->app->bind(BookingStore::class, function (Application $app) {
            return new DatabaseBookingStore($app->make('db')->connection());
        });
        $this->app->bind(Transaction::class, function (Application $app) {
            return new LaravelTransaction($app->make('db')->connection());
        });
    }
}
```

Оба адаптера используют default connection. При нескольких соединениях или tenant-контексте выбор соединения должен быть одинаковым для загрузки, сохранения и транзакции.

## Точка входа

Основание: [LAR-ENTRY-01](presentation.md#lar-entry-01).

Пример HTTP-контроллера предполагает маршрут с параметром `bookingId` и аутентификацию проекта. Проверка отсутствия пользователя остаётся явной.

```php
<?php

declare(strict_types=1);

namespace App\Modules\Booking\Presentation\Http\Controllers;

use App\Modules\Booking\Application\UseCases\CancelBooking\CancelBooking;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final readonly class CancelBookingController
{
    public function __construct(private CancelBooking $cancelBooking) {}

    public function __invoke(Request $request, string $bookingId): JsonResponse
    {
        $user = $request->user();

        if ($user === null) {
            abort(401);
        }

        $result = $this->cancelBooking->handle(
            $bookingId,
            (string) $user->getAuthIdentifier(),
        );

        return response()->json([
            'booking_id' => $result->bookingId,
            'state' => $result->state,
        ]);
    }
}
```

В этом примере проект принимает перевод `BookingNotFound` в 404, `BookingAccessDenied` в 403, `CannotCancelBooking` и `BookingConflict` в 409. Ошибки данных и хранения обрабатываются как технические. Настройте этот перевод в обработчике исключений приложения по [LAR-ERROR-01](presentation.md#lar-error-01).

## Границы примера

- Для запуска в приложении нужны PSR-4 autoload, миграция, создание тестовой записи, регистрация провайдера, маршрут, аутентификация и перевод ошибок.
- Схема описывает только два состояния; создание записи и другие изменения здесь не реализованы.
- Время решения об отмене — момент, полученный сценарием после загрузки. Требование «успеть зафиксировать до начала» было бы другим правилом и потребовало бы дополнительного механизма.
- `readonly` у `LoadedBooking` запрещает замену ссылки, но вложенный агрегат намеренно изменяем.

## Проверки при переносе

Используйте таблицу из ядра: успех, точная граница времени, повтор, чужой пользователь, отсутствие объекта и конфликт. Дополнительно проверьте rollback, реальное сохранение и восстановление, неизвестный статус в БД и две конкурирующие операции по [LAR-TEST-02](testing.md#lar-test-02).
