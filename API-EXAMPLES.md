# Python VPC API Examples

## Storage 

### List block storage volumes

```python
list_volumes(
        self,
        *,
        start: Optional[str] = None,
        limit: Optional[int] = None,
        attachment_state: Optional[str] = None,
        encryption: Optional[str] = None,
        name: Optional[str] = None,
        operating_system_family: Optional[str] = None,
        operating_system_architecture: Optional[str] = None,
        tag: Optional[str] = None,
        zone_name: Optional[str] = None,
        **kwargs,
    ) -> DetailedResponse
```

### Get volume

```python
get_volume(
        self,
        id: str,
        **kwargs,
    ) -> DetailedResponse
```

### List volume profiles 

```python
list_volume_profiles(
        self,
        *,
        start: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs,
    ) -> DetailedResponse
```

### List File shares

```python
list_shares(
        self,
        *,
        start: Optional[str] = None,
        limit: Optional[int] = None,
        resource_group_id: Optional[str] = None,
        name: Optional[str] = None,
        sort: Optional[str] = None,
        replication_role: Optional[str] = None,
        **kwargs,
    ) -> DetailedResponse
```

### Get file share

```python
get_share(
        self,
        id: str,
        **kwargs,
    ) -> DetailedResponse
```

### Get file share profiles 

```python
list_share_profiles(
        self,
        *,
        start: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        **kwargs,
    ) -> DetailedResponse
```

