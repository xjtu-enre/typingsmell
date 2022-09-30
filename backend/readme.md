# typing-practice-analyze-service

## Api

### Project

`request_url:/project`

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "res": [
      {
        "id": 1,
        "project_name": "chainer",
        "create_at": "2021-10-26-18-24-47",
        "version": "522e017a18008ee00e39f4ae4b30f4f9db3824b2",
        "file": 3313,
        "loc": 504757,
        "type_manner": "stub&inline"
      }
    ]
  }
}
```

### Pattern

`request_url:/pattern/<project_id>`

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "pattern_count": {
      "some_metrics": 100
    },
    "pattern_info": {
      "Overload": {
        "file_path": [
          {
            "entity_type": "Function",
            "start_line": "16",
            "end_line": "18"
          },
          {
            "entity_type": "Function",
            "start_line": "16",
            "end_line": "18"
          }
        ]
      }
    }
  }
}
```

### Get file text

`request: url:/file/<project_id>`
```json
{
  "file_path": "file_path"
}
```

```json
{
  "code": 0,
  "msg": "success",
  "data": "import os\nimport subprocess\n ..."
}
```