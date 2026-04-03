# Consumer Price Index — Iceland

Annual change in the Icelandic Consumer Price Index (CPI), sourced from Statistics Iceland (Hagstofa).

## Source

**Database:** [Statice — Statistics Iceland](https://statice.is/stat-bank)

**Endpoint:**
```
https://px.hagstofa.is/pxen/pxweb/en/Efnahagur/Efnahagur__visitolur__1_vnv__1_vnv/VIS01000.px/table/tableViewLayout2/
```

## API Query

`POST` the following JSON body to the endpoint above to retrieve annual CPI change:

```json
{
  "query": [
    {
      "code": "Index",
      "selection": {
        "filter": "item",
        "values": ["CPI"]
      }
    },
    {
      "code": "Item",
      "selection": {
        "filter": "item",
        "values": ["change_A"]
      }
    }
  ],
  "response": {
    "format": "json"
  }
}
```

## Notes

- `change_A` returns the **annual percentage change** in the index.
- Response format is `json` (PX-Web API standard).
- Table ID: `VIS01000.px`
