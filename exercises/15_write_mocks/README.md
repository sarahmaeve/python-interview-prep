# Exercise 15: Write Mocks — Payment Processor

This exercise is different from the others. The code in `payment_processor.py`
is **completely correct** — there are no bugs to fix. Instead, the test file
has **incomplete mock setups** — placeholder `# TODO:` comments where mock
configuration should go. Your job is to write the mocking code so all tests
pass.

This exercises the skill of constructing mock objects, configuring return
values and side effects, and using `patch` correctly.

## Your Task

1. Read `payment_processor.py` to understand the code and its dependencies.
2. Open `test_payment_processor.py` — look for `# TODO:` comments.
3. Write the missing mock setup code at each TODO.
4. Run the tests until they all pass:

```bash
python3 -m unittest test_payment_processor
```

## Skills Practiced

- Creating `MagicMock` objects with `spec` for type safety
- Configuring `return_value` on mock methods
- Configuring `side_effect` for exceptions and call-by-call responses
- Using `@patch` as a decorator and as a context manager
- Patching module-level imports vs. instance methods
- Asserting mock call counts and arguments with `assert_called_with`,
  `assert_not_called`, and `call_count`

## Hints

- When patching, remember to patch where the name is **looked up**, not where
  it is **defined**. For example, `payment_processor.urlopen` — not
  `urllib.request.urlopen`.
- To mock a chain like `urlopen(url).read().decode()`, you need to set up
  `mock_urlopen.return_value.read.return_value.decode.return_value`.
- `side_effect` can be a list (values returned one-per-call) or an exception
  class/instance (raised on every call).
