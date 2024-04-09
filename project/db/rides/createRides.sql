DROP TABLE IF EXISTS rides;
CREATE TABLE rides (
  rideId INT         NOT NULL AUTO_INCREMENT,
  startAddress     varchar(100) NOT NULL,
  endAddress     varchar(100) NOT NULL,
  rideStatus     varchar(100) DEFAULT 'Awaiting driver',
  cost float(32) NOT NULL,
  riderId INT NOT NULL,
  driverId INT,
  FOREIGN KEY (riderId) REFERENCES users(userId) ON DELETE CASCADE,
  FOREIGN KEY (driverId) REFERENCES users(userId) ON DELETE CASCADE,
  PRIMARY KEY (rideId)
);
