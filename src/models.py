from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, BigInteger, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    __tablename__= 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255),nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), unique=False, nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), unique=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

      # Relacion inversa

    favorite: Mapped[list["Favorite"]] = relationship(
    back_populates="user")


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name
        }

    def serialize_with_favorites(self):
        
        data = self.serialize()
        data["favorites"] = [favorite.serialize_with_details() for favorite in self.favorite]
        return data
        

class Planet(db.Model):
    __tablename__= 'planet'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    climate: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) 
    terrain: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)  
    population: Mapped[int] = mapped_column(BigInteger, nullable=False)  


  # Relacion inversa

    favorite: Mapped[list["Favorite"]] = relationship(
    back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            
        }

class Character(db.Model):
    __tablename__= 'character'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)   
    height: Mapped[int] = mapped_column(Integer, nullable=False)  
    mass: Mapped[int] = mapped_column(Integer, nullable=False)  

  # Relacion inversa

    favorite: Mapped[list["Favorite"]] = relationship(
    back_populates="character")


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass,
            
        }


class Vehicle(db.Model):
    __tablename__= 'vehicle'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    cargo_capacity: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)   
    length: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) 
    model: Mapped[str] = mapped_column(String(100), unique=True, nullable=False) 

  # Relacion inversa

    favorite: Mapped[list["Favorite"]] = relationship(
    back_populates="vehicle")



    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "cargo_capacity": self.cargo_capacity,
            "length": self.length,
            "model": self.model,
        }

class Favorite(db.Model):
    __tablename__= 'favorite'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'), nullable=True)
    character_id: Mapped[int] = mapped_column(ForeignKey('character.id'), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicle.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

     # Relaciones 

    user: Mapped["User"] = relationship(
    "User",
    back_populates="favorite"
    )
    planet: Mapped["Planet"] = relationship(
    "Planet",
    back_populates="favorite"
    )

    character: Mapped["Character"] = relationship(
    "Character",
    back_populates="favorite"
    )

    vehicle: Mapped["Vehicle"] = relationship(
    "Vehicle",
    back_populates="favorite"
    )


    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
            "vehicle_id": self.vehicle_id,
            "created_at": self.created_at.isoformat(),
        }


    def serialize_with_details(self):
        
      
        data = self.serialize()
        if self.planet:
            data["planet"] = self.planet.serialize()
        if self.character:
            data["character"] = self.character.serialize()
        if self.vehicle:
            data["vehicle"] = self.vehicle.serialize()
        return data
    
   

