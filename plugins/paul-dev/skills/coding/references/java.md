# Java 25 and Spring Boot 4

The Google Java Style Guide is the style authority; Effective Java (3rd ed.) is the design
authority. The project's own formatter plugin and the code already in the file win over both.
Oracle's 1999 Code Conventions are archived and not cited.

## Toolchain, September 2026

- Spring Boot 4.1.x is the upstream line (docs describe 4.1.1); Java 17 minimum, runs to Java 26,
  needs Spring Framework 7.0.9+.
- Java 25 is LTS, GA 2025-09-16. Finalized in 25: JEP 511 module imports, JEP 512 compact
  source files, JEP 513 flexible constructor bodies.
- Boot 4 ships Jackson 3: `tools.jackson.*`, not `com.fasterxml.jackson.*`; only annotations
  stay under `com.fasterxml.jackson.annotation`. Exceptions unchecked; `asText()` is `asString()`.
- Java 25 disables implicit annotation processing: Lombok needs an explicit
  `annotationProcessorPaths` entry or generates nothing.
- Tests: JUnit 5 (5.13.x), AssertJ, Mockito, all via `spring-boot-starter-test`.
- Build: Maven, `mvn -q verify`. Run the project's formatter plugin if it has one, never
  hand-format.

## Conventions

- Google Java Style: classes UpperCamelCase nouns; methods lowerCamelCase verbs; constants
  UPPER_SNAKE_CASE only for `static final` immutable values; packages lowercase, no underscores.
- Records for immutable DTOs (JEP 395); sealed interfaces for closed hierarchies (JEP 409);
  pattern matching for exhaustive `switch` (JEP 441).
- `var` when the right side makes the type obvious (JEP 286); text blocks for multi-line
  strings (JEP 378); `_` for unused patterns (JEP 456); virtual threads for blocking I/O
  (JEP 444), via `spring.threads.virtual.enabled=true`.
- Effective Java Item 17: minimize mutability. Item 18: favor composition over inheritance.
- Effective Java Item 45: streams judiciously, a plain loop for side effects or early exit.
  Item 55: `Optional` judiciously, never as a field or parameter.
- Spring "generally advocates constructor injection"; one constructor needs no `@Autowired`;
  injected fields are `final`.
- Layering: controller, service, repository. Controllers return records or DTOs, never
  entities.
- Exceptions: unchecked, mapped in one `@RestControllerAdvice`.
- `java.time` (`Instant`, `LocalDate`, `Duration`), never `java.util.Date` or `Calendar`.
- SLF4J: `private static final Logger log = LoggerFactory.getLogger(Foo.class)`; never `System.out`.
- Class-based proxies: a service needs no interface until a second implementation exists.

## Testing

- JUnit 5 `@Test`; the method name is the behaviour (`returnsEmptyWhenNoMatches`) or a
  `@DisplayName` sentence.
- AssertJ: `assertThat(actual).isEqualTo(expected)`, `assertThatThrownBy(...)`; not bare
  `assertNotNull`.
- Slices before the full context: `@WebMvcTest`, `@DataJpaTest`; `@SpringBootTest` only for
  wiring itself.
- Run `mvn -q verify`, not a single test class, before reporting.

## What AI code gets wrong here

| Does | Instead |
|---|---|
| `@Autowired` on fields | Constructor injection with `final` fields. |
| Returns a JPA entity from a controller | A record or DTO; entities leak schema and lazy-loading. |
| Lombok `@Data` or `@EqualsAndHashCode` on an entity | No Lombok equality on entities; records for DTOs. |
| `Optional` as a field or parameter, or bare `.get()` | Return type only; `orElseThrow`, `map`, `orElse`. |
| JPQL or SQL built by string concatenation | Named parameters or Spring Data derived queries. |
| `@Transactional` on a private or self-invoked method | A public method through the proxy; self-invocation skips it. |
| `FooService` interface plus one `FooServiceImpl` | One class. |
| `com.fasterxml.jackson` imports in Boot 4 | `tools.jackson`. |
| `catch (Exception e)` that logs and continues, or rethrows with no message | Catch the specific type, or propagate. |
| `java.util.Date` | `java.time`. |
| `System.out.println` | The SLF4J logger. |
| Lombok on Java 25 without `annotationProcessorPaths` | The compiler-plugin entry. |

## Sources

- Google Java Style Guide: https://google.github.io/styleguide/javaguide.html
- Spring Framework, Dependency Injection: https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html
- Spring Boot system requirements: https://docs.spring.io/spring-boot/system-requirements.html
- Introducing Jackson 3 support in Spring (2025-10-07): https://spring.io/blog/2025/10/07/introducing-jackson-3-support-in-spring/
- JDK 25 project page: https://openjdk.org/projects/jdk/25/
- JUnit 5 User Guide: https://docs.junit.org/current/user-guide/
- Effective Java, 3rd ed.: https://www.oreilly.com/library/view/effective-java-3rd/9780134686097/
