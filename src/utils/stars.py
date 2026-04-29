"""
stars.py — NorthStar Property Management
Easter egg module. You found it. That means you read the README raw.
That's exactly the kind of operator this tool was built for.
"""

NORTH_STAR = "Polaris"
CONSTELLATION = "Ursa Minor"

LORE = """
    ✦  ·  ·  ·  ✦  ·  ·
    ·  ·  ✦  ·  ·  ·  ✦
    ·  ✦  ·  ·  ✦  ·  ·
         ★  ← You are here
    ·  ·  ✦  ·  ·  ✦  ·
    ·  ✦  ·  ·  ·  ·  ✦

  Navigators used Polaris not because it was
  the brightest star — it isn't — but because
  it didn't move. Reliability beats brilliance.

  That's the whole philosophy of this toolkit.

  Build systems that don't move.
  The tenants, the leases, the vendors —
  those all change. Your process shouldn't.

  99%+ uptime isn't luck. It's discipline.
  ⭐
"""

def find_north():
    print(f"\n  The North Star is {NORTH_STAR}, in {CONSTELLATION}.\n")
    print(LORE)
    print("  — NorthStar Property Management\n")


if __name__ == "__main__":
    find_north()
