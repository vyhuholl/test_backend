"""Seed data script for organisations, buildings, and activities."""

import asyncio

from app.database import AsyncSessionLocal
from app.models.activity import Activity
from app.models.building import Building
from app.models.organisation import Organisation, OrganisationPhone


async def seed_data() -> None:
    """Seed the database with initial data."""
    async with AsyncSessionLocal() as session:
        # Create buildings
        building1 = Building(
            address="123 Main Street, Moscow, Russia",
            latitude=55.7558,
            longitude=37.6173,
        )
        building2 = Building(
            address="456 Innovation Avenue, St. Petersburg, Russia",
            latitude=59.9343,
            longitude=30.3351,
        )
        building3 = Building(
            address="789 Tech Boulevard, Novosibirsk, Russia",
            latitude=55.0084,
            longitude=82.9237,
        )
        session.add_all([building1, building2, building3])
        await session.flush()

        # Create activities (3-level hierarchy)
        # Level 1 activities
        healthcare = Activity(name="Healthcare")
        education = Activity(name="Education")
        retail = Activity(name="Retail")
        technology = Activity(name="Technology")
        finance = Activity(name="Finance")
        session.add_all([healthcare, education, retail, technology, finance])
        await session.flush()

        # Level 2 activities
        hospitals = Activity(name="Hospitals", parent_id=healthcare.id)
        schools = Activity(name="Schools", parent_id=education.id)
        supermarkets = Activity(name="Supermarkets", parent_id=retail.id)
        software = Activity(name="Software", parent_id=technology.id)
        banks = Activity(name="Banks", parent_id=finance.id)
        session.add_all([hospitals, schools, supermarkets, software, banks])
        await session.flush()

        # Level 3 activities
        clinics = Activity(name="Clinics", parent_id=hospitals.id)
        universities = Activity(name="Universities", parent_id=schools.id)
        pharmacies = Activity(name="Pharmacies", parent_id=supermarkets.id)
        startups = Activity(name="Startups", parent_id=software.id)
        insurance = Activity(name="Insurance", parent_id=banks.id)
        session.add_all(
            [clinics, universities, pharmacies, startups, insurance]
        )
        await session.flush()

        # Create organisations
        org1 = Organisation(
            name="MediCare Clinic",
            building_id=building1.id,
        )
        org2 = Organisation(
            name="Tech University",
            building_id=building2.id,
        )
        org3 = Organisation(
            name="FoodMart Supermarket",
            building_id=building1.id,
        )
        org4 = Organisation(
            name="SoftDev Startup",
            building_id=building3.id,
        )
        org5 = Organisation(
            name="City Hospital",
            building_id=building2.id,
        )
        session.add_all([org1, org2, org3, org4, org5])
        await session.flush()

        # Add phone numbers
        phone1 = OrganisationPhone(
            organisation_id=org1.id,
            phone_number="+7 (495) 123-45-67",
        )
        phone2 = OrganisationPhone(
            organisation_id=org1.id,
            phone_number="+7 (495) 987-65-43",
        )
        phone3 = OrganisationPhone(
            organisation_id=org2.id,
            phone_number="+7 (812) 555-12-34",
        )
        phone4 = OrganisationPhone(
            organisation_id=org3.id,
            phone_number="+7 (383) 111-22-33",
        )
        phone5 = OrganisationPhone(
            organisation_id=org4.id,
            phone_number="+7 (999) 000-00-00",
        )
        session.add_all([phone1, phone2, phone3, phone4, phone5])
        await session.flush()

        # Add activities to organisations
        org1.activities.extend([healthcare, hospitals])
        org2.activities.extend([education, universities])
        org3.activities.extend([retail, supermarkets])
        org4.activities.extend([healthcare, clinics])
        org5.activities.extend([technology, software, startups])

        await session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
