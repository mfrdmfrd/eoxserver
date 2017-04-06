from django.test import TransactionTestCase
from django.contrib.gis.geos import Polygon, MultiPolygon

from eoxserver.core.util.timetools import parse_iso8601
from eoxserver.resources.coverages import models
from eoxserver.services import ecql


class ECQLTestCase(TransactionTestCase):
    mapping = {
        "identifier": "identifier",
        "id": "identifier",
        "beginTime": "begin_time",
        "endTime": "end_time",
        "footprint": "footprint",
        "parentIdentifier": "metadata__parent_identifier",
        "illuminationAzimuthAngle": "metadata__illumination_azimuth_angle",
        "illuminationZenithAngle": "metadata__illumination_zenith_angle",
        "illuminationElevationAngle": "metadata__illumination_elevation_angle"
    }

    def setUp(self):
        p = parse_iso8601
        range_type = models.RangeType.objects.create(name="RGB")
        # models.RectifiedDataset.objects.create(
        #     identifier="A",
        #     footprint=MultiPolygon(Polygon.from_bbox((0, 0, 5, 5))),
        #     begin_time=p("2000-01-01T00:00:00Z"),
        #     end_time=p("2000-01-01T00:00:05Z"),
        #     srid=4326, min_x=0, min_y=0, max_x=5, max_y=5,
        #     size_x=100, size_y=100,
        #     range_type=range_type
        # )

        self.create(dict(
            identifier="A",
            footprint=MultiPolygon(Polygon.from_bbox((0, 0, 5, 5))),
            begin_time=p("2000-01-01T00:00:00Z"),
            end_time=p("2000-01-01T00:00:05Z"),
            srid=4326, min_x=0, min_y=0, max_x=5, max_y=5,
            size_x=100, size_y=100,
            range_type=range_type
        ), dict(
            illumination_azimuth_angle=10.0,
            illumination_zenith_angle=20.0,
            illumination_elevation_angle=30.0,
            parent_identifier="AparentA",
        ))

        self.create(dict(
            identifier="B",
            footprint=MultiPolygon(Polygon.from_bbox((5, 5, 10, 10))),
            begin_time=p("2000-01-01T00:00:05Z"),
            end_time=p("2000-01-01T00:00:10Z"),
            srid=4326, min_x=5, min_y=5, max_x=10, max_y=10,
            size_x=100, size_y=100,
            range_type=range_type
        ), dict(
            illumination_azimuth_angle=20.0,
            illumination_zenith_angle=30.0,
            parent_identifier="BparentB",
        ))

    def create(self, coverage_params, metadata):
        c = models.RectifiedDataset.objects.create(**coverage_params)
        models.CoverageMetadata.objects.create(
            coverage=c, **metadata
        )
        return c

    def create_opt(self, coverage_params, metadata):
        pass

    def create_sar(self, coverage_params, metadata):
        pass

    def evaluate(self, cql_expr, expected_ids):
        qs = models.RectifiedDataset.objects.filter(
            ecql.parse(cql_expr, self.mapping)
        )

        # print qs.query
        self.assertItemsEqual(
            expected_ids, qs.values_list("identifier", flat=True)
        )

    # # common comparisons

    # def test_id_eq(self):
    #     self.evaluate(
    #         'identifier = "A"',
    #         ('A',)
    #     )

    # def test_id_ne(self):
    #     self.evaluate(
    #         'identifier <> "B"',
    #         ('A',)
    #     )

    # def test_float_lt(self):
    #     self.evaluate(
    #         'illuminationZenithAngle < 30',
    #         ('A',)
    #     )

    # def test_float_le(self):
    #     self.evaluate(
    #         'illuminationZenithAngle <= 20',
    #         ('A',)
    #     )

    # def test_float_gt(self):
    #     self.evaluate(
    #         'illuminationZenithAngle > 20',
    #         ('B',)
    #     )

    # def test_float_ge(self):
    #     self.evaluate(
    #         'illuminationZenithAngle >= 30',
    #         ('B',)
    #     )

    # def test_float_between(self):
    #     self.evaluate(
    #         'illuminationZenithAngle BETWEEN 19 AND 21',
    #         ('A',)
    #     )

    # # (NOT) LIKE | ILIKE

    # def test_like_beginswith(self):
    #     self.evaluate(
    #         'parentIdentifier LIKE "A%"',
    #         ('A',)
    #     )

    # def test_ilike_beginswith(self):
    #     self.evaluate(
    #         'parentIdentifier ILIKE "a%"',
    #         ('A',)
    #     )

    # def test_like_endswith(self):
    #     self.evaluate(
    #         'parentIdentifier LIKE "%A"',
    #         ('A',)
    #     )

    # def test_ilike_endswith(self):
    #     self.evaluate(
    #         'parentIdentifier ILIKE "%a"',
    #         ('A',)
    #     )

    # def test_like_middle(self):
    #     self.evaluate(
    #         'parentIdentifier LIKE "%parent%"',
    #         ('A', 'B')
    #     )

    # def test_ilike_middle(self):
    #     self.evaluate(
    #         'parentIdentifier ILIKE "%PaReNT%"',
    #         ('A', 'B')
    #     )

    # def test_not_like_beginswith(self):
    #     self.evaluate(
    #         'parentIdentifier NOT LIKE "B%"',
    #         ('A',)
    #     )

    # def test_not_ilike_beginswith(self):
    #     self.evaluate(
    #         'parentIdentifier NOT ILIKE "b%"',
    #         ('A',)
    #     )

    # def test_not_like_endswith(self):
    #     self.evaluate(
    #         'parentIdentifier NOT LIKE "%B"',
    #         ('A',)
    #     )

    # def test_not_ilike_endswith(self):
    #     self.evaluate(
    #         'parentIdentifier NOT ILIKE "%b"',
    #         ('A',)
    #     )

    # # (NOT) IN

    # def test_string_in(self):
    #     self.evaluate(
    #         'identifier IN ("A", \'B\')',
    #         ('A', 'B')
    #     )

    # def test_string_not_in(self):
    #     self.evaluate(
    #         'identifier NOT IN ("B", \'C\')',
    #         ('A',)
    #     )

    # # (NOT) NULL

    # def test_string_null(self):
    #     self.evaluate(
    #         'illuminationElevationAngle IS NULL',
    #         ('B',)
    #     )

    # def test_string_not_null(self):
    #     self.evaluate(
    #         'illuminationElevationAngle IS NOT NULL',
    #         ('A',)
    #     )

    # # temporal predicates

    # def test_before(self):
    #     self.evaluate(
    #         'beginTime BEFORE 2000-01-01T00:00:01Z',
    #         ('A',)
    #     )

    # def test_before_or_during_dt_dt(self):
    #     self.evaluate(
    #         'beginTime BEFORE OR DURING '
    #         '2000-01-01T00:00:00Z / 2000-01-01T00:00:01Z',
    #         ('A',)
    #     )

    # def test_before_or_during_dt_td(self):
    #     self.evaluate(
    #         'beginTime BEFORE OR DURING '
    #         '2000-01-01T00:00:00Z / PT4S',
    #         ('A',)
    #     )

    # def test_before_or_during_td_dt(self):
    #     self.evaluate(
    #         'beginTime BEFORE OR DURING '
    #         'PT4S / 2000-01-01T00:00:03Z',
    #         ('A',)
    #     )

    # def test_during_td_dt(self):
    #     self.evaluate(
    #         'beginTime BEFORE OR DURING '
    #         'PT4S / 2000-01-01T00:00:03Z',
    #         ('A',)
    #     )

    # TODO: test DURING OR AFTER / AFTER

    # # spatial predicates

    # def test_intersects_point(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, POINT(1 1))',
    #         ('A',)
    #     )

    # def test_intersects_mulitipoint_1(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, MULTIPOINT(0 0, 1 1))',
    #         ('A',)
    #     )

    # def test_intersects_mulitipoint_2(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, MULTIPOINT((0 0), (1 1)))',
    #         ('A',)
    #     )

    # def test_intersects_linestring(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, LINESTRING(0 0, 1 1))',
    #         ('A',)
    #     )

    # def test_intersects_multilinestring(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, MULTILINESTRING((0 0, 1 1), (2 1, 1 2)))',
    #         ('A',)
    #     )

    # def test_intersects_polygon(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, '
    #         'POLYGON((0 0, 3 0, 3 3, 0 3, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1)))',
    #         ('A',)
    #     )

    # def test_intersects_multipolygon(self):
    #     self.evaluate(
    #         'INTERSECTS(footprint, '
    #         'POLYGON((0 0, 3 0, 3 3, 0 3, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1)))',
    #         ('A',)
    #     )

    # # TODO: other relation methods

    # arithmethic expressions

    def test_arith_simple_plus(self):
        self.evaluate(
            'illuminationZenithAngle = 10 + 10',
            ('A',)
        )

    def test_arith_field_plus_1(self):
        self.evaluate(
            'illuminationZenithAngle = illuminationAzimuthAngle + 10',
            ('A', 'B')
        )

    def test_arith_field_plus_2(self):
        self.evaluate(
            'illuminationZenithAngle = 10 + illuminationAzimuthAngle',
            ('A', 'B')
        )

