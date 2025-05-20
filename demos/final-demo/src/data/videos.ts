export const videoData = [
  {
    id: "el_PChGfJN8",
    title: "HELLUVA BOSS - Murder Family // S1: Episode 1",
    duration: 822,
  },
  {
    id: "kpnwRg268FQ",
    title: "HELLUVA BOSS - Loo Loo Land // S1: Episode 2",
    duration: 973,
  },
  {
    id: "RghsgkZKedg",
    title: "HELLUVA BOSS - Spring Broken // S1: Episode 3",
    duration: 1046,
  },
  {
    id: "1ZFseYPmkAk",
    title: "HELLUVA BOSS - C.H.E.R.U.B // S1: Episode 4",
    duration: 915,
  },
  {
    id: "h2ZmVAdezF8",
    title: "HELLUVA BOSS - The Harvest Moon Festival // S1: Episode 5",
    duration: 1084,
  },
  {
    id: "yXErLiSbxXQ",
    title: "HELLUVA BOSS - Truth Seekers // S1: Episode 6",
    duration: 1349,
  },
  {
    id: "8zyGQquL8VM",
    title: "HELLUVA BOSS - OZZIE'S // S1: Episode 7 - FINALE",
    duration: 1009,
  },
  {
    id: "D-2799Y07Zc",
    title: "HELLUVA BOSS - QUEEN BEE // S1: Episode 8",
    duration: 948,
  },
  {
    id: "_spuxXnul0U",
    title: "HELLUVA BOSS - THE CIRCUS // S2: Episode 1",
    duration: 1385,
  },
  {
    id: "4J0xFUyz1nw",
    title: "HELLUVA BOSS - SEEING STARS // S2: Episode 2",
    duration: 1260,
  },
  {
    id: "j1BfO7VlIw4",
    title: "HELLUVA BOSS - EXES AND OOHS // S2: Episode 3",
    duration: 1509,
  },
  {
    id: "KJy7T24rhg0",
    title: "HELLUVA BOSS - WESTERN ENERGY // S2: Episode 4",
    duration: 1166,
  },
  {
    id: "lYu1ysDULwA",
    title: "HELLUVA BOSS - UNHAPPY CAMPERS // S2: Episode 5",
    duration: 1260,
  },
  {
    id: "y1sF6ZeASU0",
    title: "HELLUVA BOSS - OOPS // S2: Episode 6",
    duration: 1620,
  },
  {
    id: "rRymSi8SmqA",
    title:
      "HELLUVA BOSS - MAMMON’S MAGNIFICENT MUSICAL MID-SEASON SPECIAL (ft Fizzarolli)  // S2: Episode 7",
    duration: 1830,
  },
  {
    id: "Fj9YRsV1pEw",
    title: "HELLUVA BOSS - THE FULL MOON  // S2: Episode 8",
    duration: 1390,
  },
  {
    id: "tLD-OUkYtk4",
    title: "HELLUVA BOSS - APOLOGY TOUR  // S2: Episode 9",
    duration: 1315,
  },
  {
    id: "5DV4IIKwqRI",
    title: "HELLUVA BOSS - GHOSTF**KERS // S2: Episode 10",
    duration: 1645,
  },
  {
    id: "IoVB5Hn2m_k",
    title: "HELLUVA BOSS - MASTERMIND // S2: Episode 11",
    duration: 1320,
  },
  {
    id: "GisSNuVpbkM",
    title: "HELLUVA BOSS - SINSMAS // S2: Episode 12 -FINALE",
    duration: 1745,
  },
  {
    id: "_38dtqdR5V4",
    title: "HELLUVA SHORTS 1: HELL'S BELLES // HELLUVA BOSS",
    duration: 355,
  },
  {
    id: "uSDG4K1ycvc",
    title: "HELLUVA SHORTS 2 // MISSION: ANTARCTICA // HELLUVA BOSS",
    duration: 260,
  },
  {
    id: "3-NrCcr8Bcg",
    title: "HELLUVA SHORTS 3 // MISSION: WEEABOO-BOO // HELLUVA BOSS",
    duration: 280,
  },
  {
    id: "pngogrW4iC4",
    title: "HELLUVA SHORTS 4 // MISSION: CHUPACABRAS // HELLUVA BOSS",
    duration: 392,
  },
] as const;

export const videosById = new Map<string, (typeof videoData)[number]>();
videoData.forEach((video) => videosById.set(video.id, video));
