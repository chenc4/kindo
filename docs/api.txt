# API V1

## search

| METHOD |    PATH    |
|--------|------------|
| GET    | /v1/search |

|   NAME   |  TYPE  | DEFAULT | MUST |       DESCRIPTION        |
|----------|--------|---------|------|--------------------------|
| username | string |         | no   | account username         |
| token    | string |         | no   | account password's token |
| q        | string |         | yes  | image name               |

response:

|    NAME   |  TYPE  | DEFAULT | MUST |    DESCRIPTION     |
|-----------|--------|---------|------|--------------------|
| name      | string |         | yes  | image name         |
| version   | string |         | yes  | image version      |
| url       | string |         | yes  | image download url |
| author    | string |         | yes  | image author       |
| size      | string |         | yes  | image size         |
| buildtime | string |         | yes  | image build time   |

## pull

| METHOD |   PATH   |
|--------|----------|
| GET    | /v1/pull |

|   NAME   |  TYPE  | DEFAULT | MUST |       DESCRIPTION        |
|----------|--------|---------|------|--------------------------|
| username | string |         | no   | account username         |
| token    | string |         | no   | account password's token |
| author   | string |         | no   | image author             |
| version  | string |         | no   | image version            |
| name     | string |         | yes  | image name               |
| code     | string |         | no   | extraction code          |

response:

|    NAME   |  TYPE  | DEFAULT | MUST |    DESCRIPTION     |
|-----------|--------|---------|------|--------------------|
| name      | string |         | yes  | image name         |
| version   | string |         | yes  | image version      |
| url       | string |         | yes  | image download url |
| author    | string |         | yes  | image author       |
| size      | string |         | yes  | image size         |
| buildtime | string |         | yes  | image build time   |

## register

| METHOD |     PATH     |
|--------|--------------|
| POST   | /v1/register |

|   NAME   |  TYPE  | DEFAULT | MUST |   DESCRIPTION    |
|----------|--------|---------|------|------------------|
| username | string |         | yes  | account username |
| password | string |         | yes  | account password |

response:

|   NAME   |  TYPE  | DEFAULT | MUST | DESCRIPTION  |
|----------|--------|---------|------|--------------|
| uid      | string |         | yes  | account id   |
| username | string |         | yes  | account name |

## push

| METHOD |   PATH   |
|--------|----------|
| POST   | /v1/push |

|   NAME   |  TYPE  | DEFAULT | MUST |       DESCRIPTION        |
|----------|--------|---------|------|--------------------------|
| username | string |         | no   | account username         |
| token    | string |         | no   | account password's token |
| file     | stream |         | yes  | kindo image stream       |

response:

|   NAME  |  TYPE  | DEFAULT | MUST |  DESCRIPTION  |
|---------|--------|---------|------|---------------|
| author  | string |         | yes  | image author  |
| version | string |         | yes  | image version |
| name    | string |         | yes  | image name    |
