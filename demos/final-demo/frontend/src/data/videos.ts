export const videoData = [
  { id: "JOddp-nlNvQ", title: "Thor - Trailer (OFFICIAL)", duration: 153 },
  {
    id: "JerVrbLldXw",
    title: "Captain America: The First Avenger - Trailer",
    duration: 151,
  },
  {
    id: "eOrNdBpGMv8",
    title: "Marvel's The Avengers - Trailer (OFFICIAL)",
    duration: 125,
  },
  {
    id: "f_h95mEd4TI",
    title: "Marvel's Iron Man 3 Domestic Trailer (OFFICIAL)",
    duration: 126,
  },
  {
    id: "npvJ9FTgZbM",
    title: "Thor: The Dark World Official Trailer HD",
    duration: 151,
  },
  {
    id: "tbayiPxkUMM",
    title: "Captain America: The Winter Soldier - Trailer 1",
    duration: 153,
  },
  {
    id: "d96cjJhvlMA",
    title: "Guardians of the Galaxy - Trailer 1 (OFFICIAL)",
    duration: 151,
  },
  {
    id: "tmeOjFno6Do",
    title: "Avengers: Age of Ultron - Teaser Trailer (OFFICIAL)",
    duration: 137,
  },
  { id: "xInh3VhAWs8", title: "Ant-Man - Teaser", duration: 117 },
  {
    id: "nWHUjuJ8zxE",
    title: "Jessica Jones | Official Trailer [HD] | Netflix",
    duration: 149,
  },
  {
    id: "43NWzay3W4s",
    title: "Captain America: Civil War - Trailer",
    duration: 147,
  },
  {
    id: "ORa4hPhGrpo",
    title: "Luke Cage - Official Trailer | HD",
    duration: 154,
  },
  { id: "Lt-U_t2pUHI", title: "Doctor Strange Teaser Trailer", duration: 123 },
  {
    id: "f9OKL5no-S0",
    title: "Iron Fist | Official Trailer [HD] | Netflix",
    duration: 137,
  },
  {
    id: "dW1BIid8Osg",
    title: "Guardians of the Galaxy Vol. 2 Teaser Trailer",
    duration: 133,
  },
  {
    id: "8wNgphPi5VM",
    title: "Spider-Man: Homecoming - Trailer 1",
    duration: 137,
  },
  {
    id: "jYvHxEEgrPA",
    title: "The Defenders | Official Trailer | Netflix [HD]",
    duration: 132,
  },
  {
    id: "ue80QwXMRHg",
    title: "Thor: Ragnarok Official Trailer",
    duration: 146,
  },
  {
    id: "dxWvtMOGAhw",
    title: "Black Panther Teaser Trailer [HD]",
    duration: 113,
  },
  {
    id: "Z1BCujX3pw8",
    title: "Captain Marvel - Official Trailer",
    duration: 117,
  },
  {
    id: "TcMBFSGVi1c",
    title: "Avengers: Endgame - Official Trailer",
    duration: 147,
  },
  {
    id: "VUFmhKpZKlE",
    title: "Spider-Man: Far From Home | Teaser Trailer",
    duration: 167,
  },
  {
    id: "sj9J2ecsSpo",
    title: "WandaVision | Official Trailer | Disney+",
    duration: 81,
  },
  {
    id: "IWBsDaFWyTE",
    title: "The Falcon and the Winter Soldier | Official Trailer | Disney+",
    duration: 120,
  },
  {
    id: "nW948Va-l10",
    title: "Loki | Official Trailer | Disney+",
    duration: 137,
  },
  { id: "ybji16u608U", title: "Black Widow | Official Trailer", duration: 145 },
  {
    id: "x9D0uUKJ5KI",
    title: "What If...? | Official Trailer | Disney+",
    duration: 140,
  },
  {
    id: "8YjFbMbfXaQ",
    title: "Shang-Chi and the Legend of the Ten Rings | Official Trailer",
    duration: 119,
  },
  { id: "x_me3xsvDgk", title: "Eternals | Final Trailer", duration: 172 },
  {
    id: "5VYb3B1ETlk",
    title: "Hawkeye | Official Trailer | Disney+",
    duration: 113,
  },
  {
    id: "ZYzbalQ6Lg8",
    title: "Spider-Man: No Way Home - Official Trailer",
    duration: 184,
  },
  {
    id: "aWzlQ2N6qqg",
    title: "Doctor Strange in the Multiverse of Madness | Official Trailer",
    duration: 137,
  },
  {
    id: "m9EX0f6V11Y",
    title: "Ms. Marvel | Official Trailer | Disney+",
    duration: 108,
  },
  {
    id: "Go8nTmfrQd8",
    title: "Thor: Love and Thunder | Official Trailer",
    duration: 136,
  },
  {
    id: "D7eFpRf4tac",
    title: "I Am Groot | Official Trailer | Disney+",
    duration: 64,
  },
  {
    id: "u7JsKhI2An0",
    title: "She-Hulk: Attorney at Law | Official Trailer | Disney+",
    duration: 167,
  },
  {
    id: "bLEFqhS5WmI",
    title: "Werewolf By Night | Official Trailer | Disney+",
    duration: 87,
  },
  {
    id: "OYhFFQl4fLs",
    title: "The Guardians of the Galaxy Holiday Special | Official Trailer",
    duration: 75,
  },
  {
    id: "5WfTEZJnv_8",
    title: "Ant-Man and The Wasp: Quantumania | New Trailer",
    duration: 139,
  },
];

export const videosById = new Map<string, (typeof videoData)[number]>();
videoData.forEach((video) => videosById.set(video.id, video));
