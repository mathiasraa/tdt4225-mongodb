const ObjectID = (val: any) => {};

// User Schema
[
  {
    _id: 1,
    activities: [ObjectID(1), ObjectID(2)],
    has_labels: true,
  },
];

// Activity Schema
[
  {
    _id: 1,
    user: ObjectID(1),
    transportation_mode: "bus",
    start_date_time: "2020-01-01T09:00:00+01:00",
    end_date_time: "2020-01-01T10:00:00+01:00",
    trackpoints: [
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T09:00:00+01:00",
      },
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T09:00:00+01:00",
      },
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T09:00:00+01:00",
      },
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T09:00:00+01:00",
      },
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T09:00:00+01:00",
      },
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T09:00:00+01:00",
      },
    ],
  },
  {
    _id: 2,
    user: ObjectID(1),
    transportation_mode: "walk",
    start_date_time: "2020-01-01T10:00:00+01:00",
    end_date_time: "2020-01-01T11:00:00+01:00",
    trackpoints: [
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T10:00:00+01:00",
      },
      {
        lat: 40.7128,
        lon: 74.006,
        altitude: 0,
        date_time: "2020-01-01T10:00:00+01:00",
      },
    ],
  },
];
