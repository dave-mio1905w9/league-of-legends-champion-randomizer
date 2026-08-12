import argparse
import random
import sys
from lol_randomizer import ddragon

# Riot DDragon doesn't provide positions/lanes, so we map them based on
# common tag compositions as a fallback.
LANE_MAP = {
    "top": ["fighter", "tank"],
    "jungle": ["fighter", "assassin", "tank"],
    "mid": ["mage", "assassin"],
    "adc": ["marksman"],
    "support": ["support", "tank"]
}

def get_difficulty_tier(info):
    # Riot ranks difficulty 1-10 in info.difficulty
    diff = info.get("difficulty", 5)
    if diff <= 3:
        return "easy"
    elif diff <= 7:
        return "medium"
    else:
        return "hard"

def filter_champions(champions, tag=None, lane=None, difficulty=None):
    championPool = list(champions.values())

    if lane:
        allowed_tags = LANE_MAP.get(lane.lower(), [])
        championPool = [
            c for c in championPool
            if any(t.lower() in allowed_tags for t in c.get("tags", []))
        ]

    if tag:
        championPool = [
            c for c in championPool
            if any(t.lower() == tag.lower() for t in c.get("tags", []))
        ]

    if difficulty:
        championPool = [
            c for c in championPool
            if get_difficulty_tier(c.get("info", {})) == difficulty.lower()
        ]

    return championPool

def main():
    parser = argparse.ArgumentParser(
        description="Randomly pick League of Legends champions with smart filters."
    )
    parser.add_argument("--lane", choices=["top", "jungle", "mid", "adc", "support"], help="Filter by play lane")
    parser.add_argument("--tag", help="Filter by secondary tag (e.g. Fighter, Mage, Assassin)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], help="Filter by play difficulty")
    parser.add_argument("--count", type=int, default=1, help="Number of champions to return")
    parser.add_argument("--refresh", action="store_true", help="Force update cached data from Riot APIs")

    args = parser.parse_args()

    try:
        # We fetch from local cache or update if needed
        champions = ddragon.get_champions(force_update=args.refresh)
    except ddragon.DDragonError as err:
        print(f"Error fetching champion data: {err}", file=sys.stderr)
        sys.exit(1)

    pool = filter_champions(champions, tag=args.tag, lane=args.lane, difficulty=args.difficulty)
    
    # print(f"DEBUG: pool count is {len(pool)} out of {len(champions)}")

    if not pool:
        # TODO: If filtering returned nothing, suggest relaxing criteria instead of just quitting
        print("No champions found matching those filters.", file=sys.stderr)
        sys.exit(1)

    picks = random.sample(pool, min(args.count, len(pool)))
    for p in picks:
        info = p.get("info", {})
        diff_label = get_difficulty_tier(info)
        print(f"{p['name']} ({', '.join(p['tags'])}) - Difficulty: {diff_label}")

if __name__ == "__main__":
    main()
