"""Date parsing is independent of locale and never guesses a date."""

from casefile import dates


def test_dates():
    cases = [('03/11/2025','2025-03-11'), ('3/1/2025','2025-03-01'),
             ('2025-03-11','2025-03-11'), ('March 11, 2025','2025-03-11'),
             ('march 11, 2025','2025-03-11'), ('13/01/2025',''), ('03/11/25',''),
             ('Yesterday',''), ('','')]
    count = sum(dates.iso(value) == expected for value,expected in cases)
    print(f'dates_ok={count} of 9')
    assert count == 9, f'dates_ok={count} of 9'
    assert dates.parse('02/29/2025') is None
