-- CREATE DATABASE dbms;

-- USE dbms;

CREATE TABLE SHOP (
  ShopID INTEGER NOT NULL AUTO_INCREMENT,
  ShopName VARCHAR(60) NOT NULL,
  Location VARCHAR(255) NOT NULL,
  PRIMARY KEY(ShopID)
);

CREATE TABLE ITEMS (
  ItemID INTEGER NOT NULL AUTO_INCREMENT,
  Name VARCHAR(30) NOT NULL,
  Cost REAL NOT NULL,
  PRIMARY KEY(ItemID)
);

CREATE TABLE INVENTORY (
  ShopID INTEGER NOT NULL,
  ItemID INTEGER NOT NULL,
  Units INTEGER NOT NULL,
  FOREIGN KEY(ShopID) REFERENCES SHOP(ShopID),
  FOREIGN KEY(ItemID) REFERENCES ITEMS(ItemID),
  PRIMARY KEY(ShopID,ItemID)
);

CREATE TABLE SALES (
  ShopID INTEGER NOT NULL,
  ItemID INTEGER NOT NULL,
  Quantity INTEGER NOT NULL,
  SaleDate DATE NOT NULL,
  FOREIGN KEY(ShopID) REFERENCES SHOP(ShopID),
  FOREIGN KEY(ItemID) REFERENCES ITEMS(ItemID)
);

CREATE TABLE EMPLOYEE (
  EmpID INTEGER NOT NULL AUTO_INCREMENT,
  EmpName VARCHAR(30) NOT NULL,
  EmpPassword VARCHAR(40) NOT NULL,
  ShopID INTEGER NOT NULL,
  Username VARCHAR(50),
  PRIMARY KEY(EmpID),
  FOREIGN KEY(ShopID) REFERENCES SHOP(ShopID)
);

CREATE TABLE MANAGES (
  EmpID INTEGER NOT NULL,
  ShopID INTEGER NOT NULL,
  FOREIGN KEY(ShopID) REFERENCES SHOP(ShopID),
  FOREIGN KEY(EmpID) REFERENCES EMPLOYEE(EmpID)
);
