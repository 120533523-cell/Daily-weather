name: Daily Weather Push
on:
  schedule:
    - cron: '0 23 * * *' #  UTC时间，对应北京时间7点推送
  workflow_dispatch: # 手动测试触发
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install requests
        run: pip install requests
      - name: Run push script
        run: python push.py
        env:
          APP_ID: ${{ secrets.APP_ID }}
          APP_SECRET: ${{ secrets.APP_SECRET }}
          TEMPLATE_ID: ${{ secrets.TEMPLATE_ID }}
          OPEN_ID: ${{ secrets.OPEN_ID }}
          WEATHER_KEY: ${{ secrets.WEATHER_KEY }}
          CITY_ID: ${{ secrets.CITY_ID }}
