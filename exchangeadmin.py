import streamlit as st
import pandas as pd
from pymongo import MongoClient

@st.cache_resource
def get_mongo_collection():
    client = MongoClient(st.secrets["mongo"]["uri"])
    db = client.car_exchange
    collection = db.user_uploads
    return collection

mongo_collection = get_mongo_collection() if "mongo" in st.secrets else None

st.title("🔐 Admin Panel - Exchange App")

if mongo_collection is None:
    st.error("MongoDB is not connected. Please check your Streamlit secrets.")
    st.stop()

st.markdown("### 🧾 Registered Uploads Summary")

data = list(mongo_collection.find({}, {"_id": 0, "name": 1, "agency_id": 1, "uploads": 1}))

if not data:
    st.warning("No uploads found in the database.")
    st.stop()

records = []
for user in data:
    record = {
        "Name": user.get("name", "(unknown)"),
        "Agency ID": user.get("agency_id", "(missing)"),
        "Number of Uploads": len(user.get("uploads", []))
    }
    records.append(record)

catalog_df = pd.DataFrame(records)
st.dataframe(catalog_df)

csv = catalog_df.to_csv(index=False)
st.download_button("📥 Download Catalog as CSV", data=csv, file_name="agency_catalog.csv", mime="text/csv")

st.markdown("---")
st.markdown("### 📊 Current Data Overview")

total_uploads = sum(len(user.get("uploads", [])) for user in data)
total_users = len(data)
total_offers = 0
total_wants = 0

for user in data:
    for upload in user.get("uploads", []):
        total_offers += len(upload.get("offers", []))
        total_wants += len(upload.get("wants", []))

st.metric("Registered Agencies", total_users)
st.metric("Total Upload Events", total_uploads)
st.metric("Total Offers Uploaded", total_offers)
st.metric("Total Wants Uploaded", total_wants)

st.success("✅ Admin data view ready. Use this to audit user activity or precheck before matching.")
