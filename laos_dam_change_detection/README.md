# Water & Urban Change Detection for Huoay Lo village

Sentinel-2 change detection notebook identifying water and urban land cover shifts around a dam site in Laos between 2019 and 2020.

---

## 1. Create a Google Earth Engine account

1. Go to [earthengine.google.com](https://earthengine.google.com) and sign up for a free account.
2. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a new project. Note the **Project ID** (e.g. `my-project-123`).
3. Open the notebook and update the project ID in the first code cell:

```python
ee.Initialize(project='your-project-id')
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

GDAL is also required to export COGs (section 14 of the notebook):

```bash
# macOS
brew install gdal
```

---

## 3. Authenticate with Google Earth Engine

Run the authentication script once before opening the notebook:

```bash
python authenticate.py
```

This will open a browser window. Log in with the Google account linked to your GEE account and paste the token back into the terminal.

---

## 4. Run the notebook

```bash
jupyter notebook laos_dam_village_loss_s2_v2.ipynb
```

Run cells top to bottom. The interactive map renders inline; exported COGs are saved to the `outputs/` folder.
