from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "944d8c090733"
down_revision = "ee825378f5ee"
branch_labels = None
depends_on = None


def upgrade():
    # 🔹 Explicitly create ENUM type
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'caterer_status_enum') THEN
                CREATE TYPE caterer_status_enum AS ENUM ('pending', 'accepted', 'rejected');
            END IF;
        END$$;
        """
    )

    # 🔹 Add column using ENUM
    op.execute(
        """
        ALTER TABLE caterers
        ADD COLUMN status caterer_status_enum NOT NULL DEFAULT 'pending';
        """
    )


def downgrade():
    op.execute("ALTER TABLE caterers DROP COLUMN status;")
    op.execute("DROP TYPE IF EXISTS caterer_status_enum;")
