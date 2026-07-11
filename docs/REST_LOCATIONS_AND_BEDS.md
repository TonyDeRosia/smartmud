# Rest Locations and Beds

Rest locations are Builder/world-package content in `rest_location_profiles`. They reference canonical room features, canonical item templates, and PropertyService access profile IDs instead of creating a furniture system. Starter profiles include `ground_rest`, `basic_bed`, `inn_bed`, `property_bed`, and `bedroll_rest`.

Rest quality profiles live in `rest_quality_profiles` and adjust recovery rate only. Quality considers base quality, bed type, shelter, and future EnvironmentService/PropertyService modifiers without changing actor identity or creating alternate needs engines.
