#!/usr/bin/env python3
import pstats


p = pstats.Stats('myapp_profile.out')
print("\n\n_______________Performance Statistic_________________\n\n")
p.strip_dirs().sort_stats('cumulative').print_stats(100)

print("\n\n_______________Time spent in each function_________________\n\n")
p.sort_stats('time').print_stats(100)

print(
    f"\n\n_______________Time spent in each function"
    f"(without recursive calls)_________________\n\n")
p.sort_stats('time').print_stats(100)

print("\n\n_______________ top 10 functions calls_________________\n\n")
p.print_callers(10)
